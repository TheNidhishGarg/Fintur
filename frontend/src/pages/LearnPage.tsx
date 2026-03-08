import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "motion/react";
import { ChevronLeft, ChevronRight } from "lucide-react";

const cards = [
    {
        title: "What is a SIP?",
        subtitle: "Systematic Investment Plan",
        body: "A SIP lets you invest a fixed amount every month into a mutual fund — automatically. Instead of trying to time the market, you invest consistently regardless of market conditions. Over time, this builds wealth steadily without requiring you to watch the markets daily.",
        takeaway:
            "Start small, stay consistent — even ₹500/month compounds significantly over 10 years.",
    },
    {
        title: "Why SIP is the passive investor's best friend",
        subtitle: "Set it and forget it",
        body: "SIPs remove emotion from investing. You don't need to decide when to buy or sell. The auto-debit handles it. You also benefit from rupee cost averaging — buying more units when prices are low and fewer when they're high, which smooths out your average cost over time.",
        takeaway:
            "Rupee cost averaging means market dips actually work in your favour.",
    },
    {
        title: "Risk vs Return",
        subtitle: "What to realistically expect",
        body: "Every investment carries some risk. Higher potential returns almost always mean higher risk. As a passive investor, your goal is steady long-term growth — not quick gains. Equity mutual funds can give 10–14% annually over the long term, but may dip in the short term.",
        takeaway:
            "Don't panic at short-term dips. Time in the market beats timing the market.",
    },
    {
        title: "What is Diversification?",
        subtitle: "Don't put all your eggs in one basket",
        body: "Diversification means spreading your money across different assets, sectors and instruments. If one sector falls, others may hold steady or grow. A well-diversified portfolio reduces risk without significantly reducing returns — it's the foundation of passive investing.",
        takeaway:
            "A diversified portfolio protects you from any single market event wiping out your gains.",
    },
    {
        title: "Where will your money go?",
        subtitle: "Your investment universe",
        body: "Based on your profile, Fintur will allocate your money across mutual funds, ETFs and select large-cap stocks. Each allocation is chosen to balance growth and stability. You'll see a breakdown of exactly where every rupee goes before you confirm anything.",
        takeaway: "You stay in control — Fintur recommends, you approve.",
    },
    {
        title: "What are Mutual Funds?",
        subtitle: "Professionally managed pooled investments",
        body: "A mutual fund pools money from thousands of investors and a professional fund manager invests it across stocks, bonds or both. You buy units of the fund rather than individual stocks. This gives you instant diversification even with a small investment amount.",
        takeaway:
            "Mutual funds are ideal for passive investors — you get expert management without daily effort.",
    },
    {
        title: "What is NAV?",
        subtitle: "Net Asset Value",
        body: "NAV is the price of one unit of a mutual fund. It's calculated daily based on the total value of the fund's holdings divided by the number of units. When you invest in a mutual fund, you buy units at the current NAV. A higher NAV doesn't mean expensive — it just reflects growth.",
        takeaway:
            "NAV rising over time means your investment is growing in value.",
    },
    {
        title: "What are ETFs?",
        subtitle: "Exchange Traded Funds",
        body: "An ETF is like a mutual fund but it trades on the stock exchange like a share. It typically tracks an index like Nifty 50, meaning it holds the same stocks in the same proportion as the index. ETFs have very low fees and are one of the most efficient passive investment tools available.",
        takeaway:
            "ETFs tracking Nifty 50 have historically delivered 12–13% annual returns over the long term.",
    },
    {
        title: "A word on Stocks",
        subtitle: "Direct equity in your portfolio",
        body: "Stocks represent ownership in a company. When the company grows, so does your investment. For passive investors, Fintur recommends a small allocation to select large-cap stocks — companies with strong track records and stable growth. This adds a performance boost alongside your funds.",
        takeaway:
            "Large-cap stocks add growth potential while keeping overall portfolio risk manageable.",
    },
    {
        title: "What about IPOs?",
        subtitle: "Initial Public Offerings",
        body: "An IPO is when a private company offers its shares to the public for the first time. IPOs can offer strong early gains but also carry higher risk. For passive investors, Fintur will flag relevant IPOs for your consideration — but they are optional, never a core allocation.",
        takeaway:
            "IPOs are opportunities, not obligations — we'll surface the right ones when they appear.",
    },
];

export default function LearnPage() {
    const [current, setCurrent] = useState(0);
    const [direction, setDirection] = useState(1);
    const navigate = useNavigate();

    const card = cards[current];

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
                            <ellipse
                                cx="18"
                                cy="19.5"
                                rx="9.5"
                                ry="8"
                                fill="#5E8B7E"
                                opacity="0.96"
                            />
                            <path
                                d="M18 12 L18 27.5"
                                stroke="rgba(0,0,0,0.13)"
                                strokeWidth="0.9"
                                strokeLinecap="round"
                            />
                            <path
                                d="M10.5 17 L25.5 17"
                                stroke="rgba(0,0,0,0.13)"
                                strokeWidth="0.9"
                                strokeLinecap="round"
                            />
                            <ellipse
                                cx="18"
                                cy="8.2"
                                rx="3"
                                ry="2.5"
                                fill="#5E8B7E"
                                opacity="0.96"
                            />
                            <rect
                                x="16.3"
                                y="10.2"
                                width="3.4"
                                height="2.2"
                                rx="1.2"
                                fill="#5E8B7E"
                            />
                            <ellipse
                                cx="6.5"
                                cy="15"
                                rx="3"
                                ry="1.7"
                                transform="rotate(-35 6.5 15)"
                                fill="#5E8B7E"
                                opacity="0.88"
                            />
                            <ellipse
                                cx="29.5"
                                cy="15"
                                rx="3"
                                ry="1.7"
                                transform="rotate(35 29.5 15)"
                                fill="#5E8B7E"
                                opacity="0.88"
                            />
                            <ellipse
                                cx="7.5"
                                cy="24.5"
                                rx="2.5"
                                ry="1.6"
                                transform="rotate(35 7.5 24.5)"
                                fill="#5E8B7E"
                                opacity="0.88"
                            />
                            <ellipse
                                cx="28.5"
                                cy="24.5"
                                rx="2.5"
                                ry="1.6"
                                transform="rotate(-35 28.5 24.5)"
                                fill="#5E8B7E"
                                opacity="0.88"
                            />
                            <ellipse
                                cx="18"
                                cy="28.5"
                                rx="1.3"
                                ry="2"
                                fill="#5E8B7E"
                                opacity="0.75"
                            />
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

                    {/* Page indicator */}
                    <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                        <button
                            onClick={() => navigate("/features")}
                            style={{
                                background: "none",
                                border: "none",
                                cursor: "pointer",
                                fontFamily: "'DM Sans', sans-serif",
                                fontSize: "14px",
                                color: "#6B7A8D",
                                fontWeight: 500,
                                padding: "4px 8px",
                            }}
                        >
                            Skip
                        </button>
                        <span
                            style={{
                                fontFamily: "'DM Sans', sans-serif",
                                fontSize: "13px",
                                color: "#6B7A8D",
                            }}
                        >
                            {current + 1} of 10
                        </span>
                    </div>
                </div>

                {/* PROGRESS BAR */}
                <div style={{ display: "flex", width: "100%", height: "3px" }}>
                    {Array.from({ length: 10 }).map((_, i) => (
                        <div
                            key={i}
                            style={{
                                flex: 1,
                                background:
                                    i <= current ? "#5E8B7E" : "rgba(94,139,126,0.20)",
                                transition: "background 0.3s ease",
                            }}
                        />
                    ))}
                </div>
            </nav>

            {/* MAIN CONTENT */}
            <div
                style={{
                    paddingTop: "128px",
                    paddingLeft: "24px",
                    paddingRight: "24px",
                    paddingBottom: "48px",
                    maxWidth: "32rem",
                    marginLeft: "auto",
                    marginRight: "auto",
                }}
            >
                {/* Card + Arrows container */}
                <div
                    style={{
                        position: "relative",
                        display: "flex",
                        alignItems: "center",
                        maxWidth: "32rem",
                        marginLeft: "auto",
                        marginRight: "auto",
                    }}
                >
                    {/* LEFT ARROW */}
                    <button
                        onClick={() => {
                            setDirection(-1);
                            setCurrent(current - 1);
                        }}
                        style={{
                            position: "absolute",
                            left: "-64px",
                            width: "48px",
                            height: "48px",
                            borderRadius: "50%",
                            background: "#FFFFFF",
                            border: "2px solid rgba(94,139,126,0.20)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: "pointer",
                            boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
                            transition: "all 200ms",
                            opacity: current === 0 ? 0 : 1,
                            pointerEvents: current === 0 ? "none" : "auto",
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = "#5E8B7E";
                            e.currentTarget.style.background = "#F0F7F4";
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = "rgba(94,139,126,0.20)";
                            e.currentTarget.style.background = "#FFFFFF";
                        }}
                    >
                        <ChevronLeft size={20} color="#5E8B7E" />
                    </button>

                    {/* CARD */}
                    <div style={{ flex: 1, overflow: "hidden" }}>
                        <AnimatePresence mode="wait" custom={direction}>
                            <motion.div
                                key={current}
                                custom={direction}
                                initial={{ x: direction * 60, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                exit={{ x: direction * -60, opacity: 0 }}
                                transition={{ duration: 0.35 }}
                                style={{
                                    background: "#FFFFFF",
                                    borderRadius: "16px",
                                    padding: "32px",
                                    boxShadow: "0 8px 40px rgba(0,0,0,0.08)",
                                }}
                            >
                                {/* Pill label */}
                                <span
                                    style={{
                                        display: "inline-block",
                                        background: "rgba(94,139,126,0.10)",
                                        color: "#5E8B7E",
                                        fontFamily: "'DM Sans', sans-serif",
                                        fontSize: "12px",
                                        padding: "4px 12px",
                                        borderRadius: "9999px",
                                    }}
                                >
                                    {card.subtitle}
                                </span>

                                {/* Title */}
                                <h1
                                    style={{
                                        fontFamily: "'Playfair Display', serif",
                                        fontSize: "28px",
                                        color: "#0F1A2E",
                                        marginTop: "16px",
                                        marginBottom: "12px",
                                        lineHeight: 1.2,
                                    }}
                                >
                                    {card.title}
                                </h1>

                                {/* Body */}
                                <p
                                    style={{
                                        fontFamily: "'DM Sans', sans-serif",
                                        fontSize: "15px",
                                        color: "#6B7A8D",
                                        lineHeight: 1.7,
                                        margin: 0,
                                    }}
                                >
                                    {card.body}
                                </p>

                                {/* Divider */}
                                <div
                                    style={{
                                        marginTop: "24px",
                                        marginBottom: "16px",
                                        height: "1px",
                                        background: "rgba(0,0,0,0.06)",
                                    }}
                                />

                                {/* Takeaway box */}
                                <div
                                    style={{
                                        background: "#F0F7F4",
                                        borderRadius: "12px",
                                        padding: "16px",
                                        marginTop: "16px",
                                    }}
                                >
                                    <div
                                        style={{
                                            fontFamily: "'DM Sans', sans-serif",
                                            fontSize: "11px",
                                            fontWeight: 600,
                                            color: "#5E8B7E",
                                            textTransform: "uppercase",
                                            letterSpacing: "0.05em",
                                            marginBottom: "8px",
                                        }}
                                    >
                                        Key Takeaway
                                    </div>
                                    <p
                                        style={{
                                            fontFamily: "'DM Sans', sans-serif",
                                            fontSize: "13px",
                                            color: "#0F1A2E",
                                            lineHeight: 1.7,
                                            margin: 0,
                                        }}
                                    >
                                        {card.takeaway}
                                    </p>
                                </div>
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* RIGHT ARROW */}
                    <button
                        onClick={() => {
                            setDirection(1);
                            setCurrent(current + 1);
                        }}
                        style={{
                            position: "absolute",
                            right: "-64px",
                            width: "48px",
                            height: "48px",
                            borderRadius: "50%",
                            background: "#5E8B7E",
                            border: "none",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: "pointer",
                            boxShadow: "0 4px 16px rgba(94,139,126,0.30)",
                            transition: "all 200ms",
                            opacity: current === 9 ? 0 : 1,
                            pointerEvents: current === 9 ? "none" : "auto",
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = "#4A7A6D";
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = "#5E8B7E";
                        }}
                    >
                        <ChevronRight size={20} color="#FFFFFF" />
                    </button>
                </div>

                {/* CTA Button on last card */}
                {current === 9 && (
                    <motion.button
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.35, delay: 0.1 }}
                        onClick={() => navigate("/features")}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = "#4A7A6D";
                            e.currentTarget.style.transform = "translateY(-2px)";
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = "#5E8B7E";
                            e.currentTarget.style.transform = "translateY(0)";
                        }}
                        style={{
                            marginTop: "32px",
                            width: "100%",
                            maxWidth: "32rem",
                            marginLeft: "auto",
                            marginRight: "auto",
                            display: "block",
                            height: "56px",
                            background: "#5E8B7E",
                            color: "#FFFFFF",
                            border: "none",
                            borderRadius: "9999px",
                            fontFamily: "'Playfair Display', serif",
                            fontSize: "16px",
                            cursor: "pointer",
                            boxShadow: "0 8px 24px rgba(94,139,126,0.25)",
                            transition: "all 200ms",
                        }}
                    >
                        Explore Fintur's Features →
                    </motion.button>
                )}
            </div>
        </div>
    );
}
