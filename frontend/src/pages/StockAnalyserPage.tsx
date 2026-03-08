import { useState } from "react";
import { Search, TrendingUp, Loader2 } from "lucide-react";
import { getApiClient } from "../lib/api/client";
import { useAuthStore } from "../lib/store/authStore";

export default function StockAnalyserPage() {
    const [query, setQuery] = useState("");
    const [report, setReport] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const token = useAuthStore((state) => state.token);

    const handleAnalyze = async () => {
        if (!query.trim()) return;
        setLoading(true);
        setError(null);
        setReport(null);
        try {
            const api = getApiClient();
            const res = await api.post(
                "/api/ai/analyze-stock",
                { query },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setReport(res.data.analysis);
        } catch (err) {
            setError("Failed to analyze. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: "100vh",
            background: "#F7F6F2",
            fontFamily: "DM Sans, sans-serif",
            padding: "40px 24px",
        }}>
            <div style={{ maxWidth: "800px", margin: "0 auto" }}>
                <div style={{ marginBottom: "40px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
                        <TrendingUp size={28} color="#2D6A4F" />
                        <h1 style={{ fontSize: "28px", fontWeight: "700", color: "#1a1a1a", margin: 0 }}>
                            Stock Analyser
                        </h1>
                    </div>
                    <p style={{ color: "#6B7A8D", fontSize: "16px", margin: 0 }}>
                        Get an institutional-grade analysis of any stock
                    </p>
                </div>

                <div style={{
                    background: "#fff",
                    borderRadius: "16px",
                    padding: "24px",
                    boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
                    marginBottom: "32px",
                }}>
                    <p style={{ fontSize: "14px", color: "#6B7A8D", marginBottom: "12px", fontWeight: "500" }}>
                        Try: "Analyze Reliance Industries" or "Should I buy TCS stock?"
                    </p>
                    <div style={{ display: "flex", gap: "12px" }}>
                        <div style={{ flex: 1, position: "relative" }}>
                            <Search size={18} color="#6B7A8D" style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)" }} />
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
                                placeholder="Enter stock name or analysis question..."
                                style={{
                                    width: "100%",
                                    padding: "14px 14px 14px 44px",
                                    borderRadius: "12px",
                                    border: "1.5px solid #e0e0e0",
                                    fontSize: "15px",
                                    outline: "none",
                                    boxSizing: "border-box",
                                    fontFamily: "DM Sans, sans-serif",
                                }}
                            />
                        </div>
                        <button
                            onClick={handleAnalyze}
                            disabled={loading || !query.trim()}
                            style={{
                                background: loading ? "#ccc" : "#2D6A4F",
                                color: "#fff",
                                border: "none",
                                borderRadius: "12px",
                                padding: "14px 28px",
                                fontSize: "15px",
                                fontWeight: "600",
                                cursor: loading ? "not-allowed" : "pointer",
                                fontFamily: "DM Sans, sans-serif",
                                display: "flex",
                                alignItems: "center",
                                gap: "8px",
                                whiteSpace: "nowrap",
                            }}
                        >
                            {loading ? <Loader2 size={18} style={{ animation: "spin 1s linear infinite" }} /> : null}
                            {loading ? "Analysing..." : "Analyse"}
                        </button>
                    </div>
                </div>

                {error && (
                    <div style={{
                        background: "#fff0f0",
                        border: "1px solid #ffcccc",
                        borderRadius: "12px",
                        padding: "16px",
                        color: "#cc0000",
                        marginBottom: "24px",
                    }}>
                        {error}
                    </div>
                )}

                {loading && (
                    <div style={{
                        background: "#fff",
                        borderRadius: "16px",
                        padding: "48px 24px",
                        boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
                        textAlign: "center",
                    }}>
                        <Loader2 size={32} color="#2D6A4F" style={{ animation: "spin 1s linear infinite", marginBottom: "16px" }} />
                        <p style={{ color: "#6B7A8D", fontSize: "16px" }}>
                            Analysing {query}... This may take 30–60 seconds.
                        </p>
                    </div>
                )}

                {report && !loading && (
                    <div style={{
                        background: "#fff",
                        borderRadius: "16px",
                        padding: "32px",
                        boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
                    }}>
                        <h2 style={{ fontSize: "18px", fontWeight: "700", color: "#1a1a1a", marginBottom: "24px" }}>
                            Analysis Report
                        </h2>
                        <div style={{
                            color: "#333",
                            fontSize: "15px",
                            lineHeight: "1.8",
                            whiteSpace: "pre-wrap",
                        }}>
                            {report}
                        </div>
                    </div>
                )}
            </div>
            <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
}
