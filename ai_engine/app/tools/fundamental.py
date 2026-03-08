import pandas as pd
import requests
from bs4 import BeautifulSoup
import io
from langchain.tools import tool

@tool
def fetch_screener_fundamentals(ticker: str):
    """
    Fetches fundamental data for a given ticker from Screener.in.
    Returns a dictionary of DataFrames or an error message.
    """
    ticker = ticker.upper().replace(".NS", "").strip()
    
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
    'Connection': 'keep-alive'}
    
    url = f"https://www.screener.in/company/{ticker}/consolidated/"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() #  error for 404/500
        
        soup = BeautifulSoup(response.text, "lxml")
        
        try:
            warehouse_id = soup.find("div", id="company-info")["data-warehouse-id"]
        except (AttributeError, TypeError):
            return {"error": f"Could not extract internal ID for {ticker}. Page structure might have changed."}

        dfs = pd.read_html(io.StringIO(response.text))
        
        dfs = pd.read_html(io.StringIO(response.text))
        
        data = {}
        
        if len(dfs) >= 1: data["Quarterly_Results"] = dfs[0]
        if len(dfs) >= 2: data["Profit_Loss"] = dfs[1]
        if len(dfs) >= 3: data["Compounded_Sales_Growth"] = dfs[2]
        if len(dfs) >= 4: data["Compounded_Profit_Growth"] = dfs[3]
        if len(dfs) >= 5: data["Stock_Price_CAGR"] = dfs[4]
        if len(dfs) >= 6: data["Return_on_Equity"] = dfs[5]
        if len(dfs) >= 7: data["Balance_Sheet"] = dfs[6]
        if len(dfs) >= 8: data["Cash_Flow"] = dfs[7]
        if len(dfs) >= 9: data["Ratios"] = dfs[8]
        if len(dfs) >= 10: data["Shareholding_Quarterly"] = dfs[9]
        if len(dfs) >= 11: data["Shareholding_Yearly"] = dfs[10]

        # 3. Fetch Peers (Hidden API)
        peers_url = f"https://www.screener.in/api/company/{warehouse_id}/peers/"
        peers_res = requests.get(peers_url, headers=headers)
        
        if peers_res.status_code == 200:
            data["Peers"] = pd.read_html(io.StringIO(peers_res.text))[0]
        else:
            data["Peers_Error"] = "Could not fetch peers."

        return data

    except requests.exceptions.HTTPError:
        return {"error": f"Ticker '{ticker}' not found on Screener.in."}
    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}"}