import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "motion/react";
import {
    TrendingUp,
    BarChart2,
    PieChart,
    Search,
    LogOut,
} from "lucide-react";
import { useAuthStore } from "../lib/store/authStore.ts";

const equityCards = [
    {
        icon: Search,
        iconColor: "#5E8B7E",
        title: "Stock Analyser",
        description:
            "Deep dive into any listed stock — financials, trends, and AI insights.",
        route: "/stock-analyser",
    },
    {
        icon: BarChart2,
        iconColor: "#4F6D8A",
        title: "Portfolio X-Ray",
        description:
            "Analyse your existing stock portfolio for risk, returns and optimisation gaps.",
    },
];

const fundCards = [
    {
        icon: PieChart,
        iconColor: "#4F6D8A",
        title: "Fund Portfolio Builder",
        description:
            "Build a personalised mutual fund portfolio tailored to your goals and risk appetite.",
    },
    {
        icon: TrendingUp,
        iconColor: "#5E8B7E",
        title: "Fund Portfolio Analyser",
        description:
            "Evaluate your current mutual fund holdings — performance, overlap, and rebalancing suggestions.",
    },
];

export default function FeaturesPage() {
    const [toast, setToast] = useState(false);
    const navigate = useNavigate();
    const clearAuth = useAuthStore((state) => state.clearAuth);

    const showToast = () => {
        setToast(true);
        setTimeout(() => setToast(false), 2500);
    };

    const cardStyle: React.CSSProperties = {
        background: "#FFFFFF",
        padding: "24px",
        borderRadius: "16px",
        border: "2px solid transparent",
        cursor: "pointer",
        boxShadow: "0 4px 20px rgba(0,0,0,0.06)",
        transition: "all 250ms",
    };

    const renderCard = (
        card: { icon: React.ElementType; iconColor: string; title: string; description: string; route?: string },
        index: number
    ) => {
        const Icon = card.icon;
        return (
            <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: index * 0.1 }}
                style={cardStyle}
                onClick={() => card.route ? navigate(card.route) : showToast()}
                onMouseEnter={(e) => {
                    const el = e.currentTarget as HTMLDivElement;
                    el.style.borderColor = "#5E8B7E";
                    el.style.transform = "translateY(-4px)";
                    el.style.boxShadow = "0 8px 32px rgba(0,0,0,0.10)";
                }}
                onMouseLeave={(e) => {
                    const el = e.currentTarget as HTMLDivElement;
                    el.style.borderColor = "transparent";
                    el.style.transform = "translateY(0)";
                    el.style.boxShadow = "0 4px 20px rgba(0,0,0,0.06)";
                }}
            >
                <Icon size={28} color={card.iconColor} />
                <h3
                    style={{
                        fontFamily: "'Playfair Display', serif",
                        fontSize: "18px",
                        color: "#0F1A2E",
                        marginTop: "16px",
                        marginBottom: "8px",
                    }}
                >
                    {card.title}
                </h3>
                <p
                    style={{
                        fontFamily: "'DM Sans', sans-serif",
                        fontSize: "13px",
                        color: "#6B7A8D",
                        lineHeight: 1.7,
                        margin: 0,
                    }}
                >
                    {card.description}
                </p>
                {card.route ? (
                    <span
                        style={{
                            display: "inline-block",
                            marginTop: "16px",
                            background: "rgba(94,139,126,0.15)",
                            color: "#5E8B7E",
                            fontFamily: "'DM Sans', sans-serif",
                            fontSize: "11px",
                            padding: "2px 8px",
                            borderRadius: "9999px",
                        }}
                    >
                        Try it →
                    </span>
                ) : (
                    <span
                        style={{
                            display: "inline-block",
                            marginTop: "16px",
                            background: "rgba(214,185,123,0.15)",
                            color: "#D6B97B",
                            fontFamily: "'DM Sans', sans-serif",
                            fontSize: "11px",
                            padding: "2px 8px",
                            borderRadius: "9999px",
                        }}
                    >
                        Coming Soon
                    </span>
                )}
            </motion.div>
        );
    };

    return (
        <div
            style={{
                minHeight: "100vh",
                background: "#F7F6F2",
                fontFamily: "'DM Sans', sans-serif",
            }}
        >
            {/* NAVBAR */}
            <nav
                style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: 0,
                    zIndex: 50,
                    background: "#F7F6F2",
                }}
            >
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "16px 24px",
                    }}
                >
                    {/* Logo */}
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <svg width="24" height="24" viewBox="0 0 36 36" fill="none">
                            <ellipse cx="18" cy="19.5" rx="9.5" ry="8" fill="#5E8B7E" opacity="0.96" />
                            <path d="M18 12 L18 27.5" stroke="rgba(0,0,0,0.13)" strokeWidth="0.9" strokeLinecap="round" />
                            <path d="M10.5 17 L25.5 17" stroke="rgba(0,0,0,0.13)" strokeWidth="0.9" strokeLinecap="round" />
                            <ellipse cx="18" cy="8.2" rx="3" ry="2.5" fill="#5E8B7E" opacity="0.96" />
                            <rect x="16.3" y="10.2" width="3.4" height="2.2" rx="1.2" fill="#5E8B7E" />
                            <ellipse cx="6.5" cy="15" rx="3" ry="1.7" transform="rotate(-35 6.5 15)" fill="#5E8B7E" opacity="0.88" />
                            <ellipse cx="29.5" cy="15" rx="3" ry="1.7" transform="rotate(35 29.5 15)" fill="#5E8B7E" opacity="0.88" />
                            <ellipse cx="7.5" cy="24.5" rx="2.5" ry="1.6" transform="rotate(35 7.5 24.5)" fill="#5E8B7E" opacity="0.88" />
                            <ellipse cx="28.5" cy="24.5" rx="2.5" ry="1.6" transform="rotate(-35 28.5 24.5)" fill="#5E8B7E" opacity="0.88" />
                            <ellipse cx="18" cy="28.5" rx="1.3" ry="2" fill="#5E8B7E" opacity="0.75" />
                        </svg>
                        <span
                            style={{
                                fontFamily: "'Playfair Display', serif",
                                fontWeight: 700,
                                fontSize: "1.4rem",
                            }}
                        >
                            <span style={{ color: "#0F1A2E" }}>Fin</span>
                            <span style={{ color: "#5E8B7E" }}>tur</span>
                        </span>
                    </div>

                    {/* Logout */}
                    <button
                        onClick={() => {
                            navigate("/");
                            clearAuth();
                        }}
                        style={{
                            background: "none",
                            border: "none",
                            cursor: "pointer",
                            padding: "8px",
                            borderRadius: "8px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            transition: "background 200ms",
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = "rgba(0,0,0,0.05)";
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = "none";
                        }}
                    >
                        <LogOut size={20} color="#6B7A8D" />
                    </button>
                </div>
            </nav>

            {/* MAIN CONTENT */}
            <div
                style={{
                    maxWidth: "48rem",
                    marginLeft: "auto",
                    marginRight: "auto",
                    paddingTop: "128px",
                    paddingLeft: "24px",
                    paddingRight: "24px",
                    paddingBottom: "64px",
                }}
            >
                {/* Page heading */}
                <h1
                    style={{
                        fontFamily: "'Playfair Display', serif",
                        fontSize: "32px",
                        color: "#0F1A2E",
                        marginBottom: "8px",
                    }}
                >
                    What would you like to do today?
                </h1>
                <p
                    style={{
                        fontFamily: "'DM Sans', sans-serif",
                        fontSize: "15px",
                        color: "#6B7A8D",
                        marginBottom: "48px",
                    }}
                >
                    Choose a feature to get started.
                </p>

                {/* SECTION 1 — Equities */}
                <div>
                    <span
                        style={{
                            display: "inline-block",
                            background: "rgba(94,139,126,0.10)",
                            color: "#5E8B7E",
                            fontFamily: "'DM Sans', sans-serif",
                            fontSize: "12px",
                            fontWeight: 600,
                            padding: "4px 12px",
                            borderRadius: "9999px",
                            marginBottom: "16px",
                        }}
                    >
                        Equities
                    </span>
                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns: "1fr 1fr",
                            gap: "16px",
                        }}
                    >
                        {equityCards.map((card, i) => renderCard(card, i))}
                    </div>
                </div>

                {/* SECTION 2 — Mutual Funds */}
                <div style={{ marginTop: "40px" }}>
                    <span
                        style={{
                            display: "inline-block",
                            background: "rgba(79,109,138,0.10)",
                            color: "#4F6D8A",
                            fontFamily: "'DM Sans', sans-serif",
                            fontSize: "12px",
                            fontWeight: 600,
                            padding: "4px 12px",
                            borderRadius: "9999px",
                            marginBottom: "16px",
                        }}
                    >
                        Mutual Funds
                    </span>
                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns: "1fr 1fr",
                            gap: "16px",
                        }}
                    >
                        {fundCards.map((card, i) => renderCard(card, i + 2))}
                    </div>
                </div>
            </div>

            {/* TOAST NOTIFICATION */}
            {toast && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    style={{
                        position: "fixed",
                        bottom: "32px",
                        left: "50%",
                        transform: "translateX(-50%)",
                        background: "#0F1A2E",
                        color: "#FFFFFF",
                        fontFamily: "'DM Sans', sans-serif",
                        fontSize: "14px",
                        padding: "12px 24px",
                        borderRadius: "9999px",
                        boxShadow: "0 8px 32px rgba(0,0,0,0.20)",
                        zIndex: 100,
                        whiteSpace: "nowrap",
                    }}
                >
                    This feature is coming soon 🚀
                </motion.div>
            )}
        </div>
    );
}
