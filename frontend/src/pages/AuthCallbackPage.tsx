import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../lib/store/authStore.ts";

export default function AuthCallbackPage() {
    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const token = params.get("token");
        const userRaw = params.get("user");

        console.log("AuthCallback - token:", token);
        console.log("AuthCallback - userRaw:", userRaw);

        if (!token || !userRaw) {
            console.log("Missing token or user, redirecting to login");
            navigate("/login");
            return;
        }

        try {
            const user = JSON.parse(decodeURIComponent(userRaw));
            console.log("AuthCallback - user:", user);
            setAuth(token, user);

            if (user.tier !== null && user.tier !== undefined && user.tier !== "") {
                console.log("Already onboarded, redirecting to features");
                navigate("/features");
            } else {
                console.log("New user, redirecting to experience");
                navigate("/experience");
            }
        } catch (err) {
            console.error("Parse error:", err);
            navigate("/login");
        }
    }, []);

    return (
        <div style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "#F7F6F2",
            fontFamily: "DM Sans, sans-serif",
        }}>
            <p style={{ color: "#6B7A8D", fontSize: "16px" }}>
                Signing you in...
            </p>
        </div>
    );
}
