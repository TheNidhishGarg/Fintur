import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
from langchain.tools import tool
from typing import Optional

@tool
def fetch_technical_data(ticker: str, period: str = "5y", start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Fetches raw technical data (Candlestick + Indicators) for an Indian stock.
    Supports both "Latest" view (default) and "Historical" view (specific dates).

    Args:
        ticker (str): Stock symbol (e.g., 'RELIANCE', 'TATASTEEL').
        period (str): Data duration to fetch if no dates provided. Defaults to "5y".
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. Overrides 'period'.
        end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to today if start_date is set.

    Returns:
        dict: Contains 'Daily_Data' (sliced or specific range) and 'Weekly_Data_Full_History'.
    """
    try:
        # Standardize Ticker
        ticker = ticker.upper().strip()
        # Add .NS suffix for NSE tickers if missing
        if not ticker.endswith(".NS") and \
           not ticker.endswith(".BO"):
            ticker = ticker + ".NS"
        stock = yf.Ticker(ticker)
        
        # --- 1. FETCHING DATA ---
        # Logic: If start_date is provided, ignore 'period' and use exact dates.
        # Otherwise, use the default relative period (e.g., "5y").
        if start_date:
            df_daily = stock.history(start=start_date, end=end_date)
        else:
            df_daily = stock.history(period=period)
        
        if df_daily.empty:
            return {"error": f"No data found for {ticker}."}

        # --- 2. RESAMPLING (Context) ---
        # We always want weekly context derived from the fetched daily range
        df_weekly = df_daily.resample('W').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        })

        # --- 3. CALCULATE INDICATORS ---
        def calc_indicators(df):
            if df.empty: return df
            
            # Trends
            df['EMA_20'] = ta.ema(df['Close'], length=20)
            df['EMA_50'] = ta.ema(df['Close'], length=50)
            df['SMA_200'] = ta.sma(df['Close'], length=200)
            
            # Momentum
            df['RSI'] = ta.rsi(df['Close'], length=14)
            macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
            df = df.join(macd)
            
            # Volatility
            bbands = ta.bbands(df['Close'], length=20, std=2)
            df = df.join(bbands)
            df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
            
            return df

        # Calculate on FULL fetched range first for accuracy
        df_daily = calc_indicators(df_daily)
        df_weekly = calc_indicators(df_weekly)

        # --- 4. SMART SLICING ---
        # If user asked for specific dates (Backtesting), give them the WHOLE daily range asked.
        # If user used default period (Dashboarding), keep only last 1 year to save tokens.
        if start_date:
            df_daily_target = df_daily.copy() 
        else:
            df_daily_target = df_daily.tail(252).copy()

        # --- HELPER: CLEAN & FORMAT ---
        def clean_df(df):
            if df.empty: return []
            
            # Dynamic Column Mapping to handle varied library outputs
            bbu = [c for c in df.columns if c.startswith('BBU')][0] if any(c.startswith('BBU') for c in df.columns) else 'BBU'
            bbl = [c for c in df.columns if c.startswith('BBL')][0] if any(c.startswith('BBL') for c in df.columns) else 'BBL'
            
            cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'EMA_20', 'EMA_50', 'SMA_200', 
                    'RSI', 'MACD_12_26_9', 'MACDs_12_26_9', 'ATR', bbu, bbl]
            
            final_cols = [c for c in cols if c in df.columns]
            df_clean = df[final_cols].copy()
            
            # Rename
            rename_map = {'MACD_12_26_9': 'MACD_Line', 'MACDs_12_26_9': 'MACD_Signal', bbu: 'BB_Upper', bbl: 'BB_Lower'}
            df_clean.rename(columns=rename_map, inplace=True)
            
            # Format
            df_clean.reset_index(inplace=True)
            df_clean['Date'] = df_clean['Date'].astype(str)

            df_clean = df_clean.replace({np.nan: None})
            
            return df_clean.round(2).to_dict(orient='records')

        # 5. Return Optimized Bundles
        return {
            "Daily_Data": clean_df(df_daily_target), # Can be 1 year slice OR specific full range
            "Weekly_Data_Full_History": clean_df(df_weekly)
        }

    except Exception as e:
        return {"error": f"Technical data fetch failed: {str(e)}"}