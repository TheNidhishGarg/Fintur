import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import AuthCallbackPage from "./pages/AuthCallbackPage.tsx";
import ExperiencePage from "./pages/ExperiencePage.tsx";
import InvestorTypePage from "./pages/InvestorTypePage.tsx";
import LearnPage from "./pages/LearnPage.tsx";
import FeaturesPage from "./pages/FeaturesPage";
import StockAnalyserPage from "./pages/StockAnalyserPage";
import CreatePortfolioPage from "./pages/CreatePortfolioPage";
import { useAuthStore } from "./lib/store/authStore.ts";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const token = useAuthStore((state) => state.token);
    if (!token) return <Navigate to="/login" replace />;
    return <>{children}</>;
}

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/auth/callback" element={<AuthCallbackPage />} />
                <Route
                    path="/experience"
                    element={
                        <ProtectedRoute>
                            <ExperiencePage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/investor-type"
                    element={
                        <ProtectedRoute>
                            <InvestorTypePage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/learn"
                    element={
                        <ProtectedRoute>
                            <LearnPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/features"
                    element={
                        <ProtectedRoute>
                            <FeaturesPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/stock-analyser"
                    element={
                        <ProtectedRoute>
                            <StockAnalyserPage />
                        </ProtectedRoute>
                    }
                />
                <Route path="/create-portfolio" element={
                    <ProtectedRoute><CreatePortfolioPage /></ProtectedRoute>
                } />
            </Routes>
        </BrowserRouter>
    );
}
