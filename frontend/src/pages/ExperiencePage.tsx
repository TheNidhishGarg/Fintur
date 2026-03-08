import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useAuthStore } from "../lib/store/authStore.ts";
import axios from "axios";

export default function ExperiencePage() {
    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);
    const token = useAuthStore((state) => state.token);

    const [step, setStep] = useState(0);
    const [birthYear, setBirthYear] = useState(1995);
    const [maritalStatus, setMaritalStatus] = useState("");
    const [occupation, setOccupation] = useState("");
    const [experienceLevel, setExperienceLevel] = useState("");
    const [loading, setLoading] = useState(false);

    const scrollRef = useRef<HTMLDivElement>(null);
    const ITEM_HEIGHT = 48;
    const CONTAINER_HEIGHT = 280;
    const VISIBLE_ITEMS = Math.floor(CONTAINER_HEIGHT / ITEM_HEIGHT); // 5
    const PADDING_ITEMS = Math.floor(VISIBLE_ITEMS / 2); // 2
    const YEARS = Array.from({ length: 2007 - 1950 + 1 }, (_, i) => 1950 + i);

    useEffect(() => {
        if (scrollRef.current && step === 0) {
            const index = YEARS.indexOf(birthYear);
            scrollRef.current.scrollTop = index * ITEM_HEIGHT;
        }
    }, [step]);

    const handleScroll = () => {
        if (!scrollRef.current) return;
        const index = Math.round(scrollRef.current.scrollTop / ITEM_HEIGHT);
        if (index >= 0 && index < YEARS.length) {
            setBirthYear(YEARS[index]);
        }
    };

    const handleYearClick = (year: number) => {
        setBirthYear(year);
        if (scrollRef.current) {
            const index = YEARS.indexOf(year);
            scrollRef.current.scrollTo({
                top: index * ITEM_HEIGHT,
                behavior: "smooth"
            });
        }
    };

    const handleNext = async () => {
        if (step < 3) {
            setStep(step + 1);
        } else {
            setLoading(true);
            try {
                await axios.patch(
                    `${import.meta.env.VITE_API_URL || "http://localhost:4000"}/auth/profile`,
                    {
                        birth_year: birthYear,
                        marital_status: maritalStatus,
                        occupation: occupation,
                        experience_level: experienceLevel,
                    },
                    {
                        headers: { Authorization: `Bearer ${token}` }
                    }
                );
                navigate("/investor-type");
            } catch (err) {
                console.error("Failed to update profile", err);
            } finally {
                setLoading(false);
            }
        }
    };

    const handleBack = () => {
        if (step > 0) setStep(step - 1);
    };

    const isNextDisabled = () => {
        if (step === 1 && !maritalStatus) return true;
        if (step === 2 && !occupation) return true;
        if (step === 3 && !experienceLevel) return true;
        return false;
    };

    return (
        <div className="min-h-screen bg-[#F7F6F2] font-sans flex flex-col">
            {/* Nav */}
            <nav className="fixed top-0 left-0 right-0 h-16 bg-[#F7F6F2] z-50 flex items-center justify-between px-6">
                <div className="flex items-center gap-2">
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
                    <span className="font-serif font-bold text-[1.4rem] text-[#0F1A2E]">
                        Fin<span className="text-[#5E8B7E]">tur</span>
                    </span>
                </div>
                <span className="text-[#6B7A8D] text-[13px] font-medium">{step + 1} of 4</span>
            </nav>

            {/* Progress Bar */}
            <div className="fixed top-16 left-0 right-0 h-[3px] flex z-50">
                {[0, 1, 2, 3].map((i) => (
                    <div
                        key={i}
                        className={`flex-1 transition-colors duration-300 ${i <= step ? "bg-[#5E8B7E]" : "bg-[#5E8B7E]/20"}`}
                    />
                ))}
            </div>

            <main className="flex-1 flex flex-col pt-32 px-6 max-w-lg mx-auto w-full relative overflow-hidden">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={step}
                        initial={{ x: 60, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: -60, opacity: 0 }}
                        transition={{ duration: 0.35, ease: "easeOut" }}
                        className="w-full flex-1 flex flex-col"
                    >
                        {step === 0 && (
                            <div className="text-center flex-1">
                                <h1 className="font-serif text-[30px] text-[#0F1A2E] leading-tight font-bold">What year were you born?</h1>
                                <p className="text-[#6B7A8D] text-[15px] mt-2 mb-10">This helps us tailor advice for your life stage</p>

                                <div className="h-[280px] w-[160px] mx-auto overflow-hidden relative">
                                    {/* Gradients */}
                                    <div className="absolute top-0 left-0 right-0 h-[112px] z-10 pointer-events-none"
                                        style={{ background: "linear-gradient(to bottom, #F7F6F2 0%, transparent 100%)" }} />
                                    <div className="absolute bottom-0 left-0 right-0 h-[112px] z-10 pointer-events-none"
                                        style={{ background: "linear-gradient(to top, #F7F6F2 0%, transparent 100%)" }} />

                                    {/* Highlight */}
                                    <div className="absolute top-1/2 left-0 right-0 h-[48px] -translate-y-1/2 bg-[#5E8B7E]/10 rounded-xl border-y-2 border-[#5E8B7E] pointer-events-none" />

                                    <div
                                        ref={scrollRef}
                                        onScroll={handleScroll}
                                        className="h-full overflow-y-scroll no-scrollbar"
                                        style={{ paddingTop: `${PADDING_ITEMS * ITEM_HEIGHT}px`, paddingBottom: `${PADDING_ITEMS * ITEM_HEIGHT}px` }}
                                    >
                                        {YEARS.map((year) => {
                                            const isSelected = year === birthYear;
                                            const isAdjacent = Math.abs(year - birthYear) === 1;
                                            return (
                                                <div
                                                    key={year}
                                                    onClick={() => handleYearClick(year)}
                                                    className={`h-[48px] flex items-center justify-center cursor-pointer transition-all ${isSelected ? "text-[#0F1A2E] text-[22px] font-bold" :
                                                        isAdjacent ? "text-[#6B7A8D] text-[16px]" :
                                                            "text-[#6B7A8D] opacity-40 text-[14px]"
                                                        }`}
                                                >
                                                    {year}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        )}

                        {step === 1 && (
                            <div className="text-center">
                                <h1 className="font-serif text-[30px] text-[#0F1A2E] leading-tight font-bold">What's your marital status?</h1>
                                <p className="text-[#6B7A8D] text-[15px] mt-2 mb-10">Financial goals often depend on family situation</p>

                                <div className="flex flex-col sm:flex-row gap-4">
                                    {[
                                        { label: "Single", emoji: "👤" },
                                        { label: "Married", emoji: "💍" },
                                        { label: "Prefer not to say", emoji: "🤐" }
                                    ].map((opt) => (
                                        <div
                                            key={opt.label}
                                            onClick={() => setMaritalStatus(opt.label)}
                                            className={`flex-1 p-6 rounded-2xl border-2 transition-all duration-200 cursor-pointer flex flex-col items-center ${maritalStatus === opt.label ? "bg-[#F0F7F4] border-[#5E8B7E]" : "bg-white border-transparent shadow-[0_4px_20px_rgba(0,0,0,0.06)]"
                                                }`}
                                        >
                                            <span className="text-3xl mb-3">{opt.emoji}</span>
                                            <span className="text-[#0F1A2E] text-[15px] font-medium">{opt.label}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {step === 2 && (
                            <div className="text-center">
                                <h1 className="font-serif text-[30px] text-[#0F1A2E] leading-tight font-bold">What do you do for a living?</h1>
                                <p className="text-[#6B7A8D] text-[15px] mt-2 mb-10">Your income type shapes your investment strategy</p>

                                <div className="grid grid-cols-2 gap-4">
                                    {[
                                        { label: "Student", emoji: "🎓" },
                                        { label: "Salaried", emoji: "🏢" },
                                        { label: "Self-Employed", emoji: "💻" },
                                        { label: "Business Owner", emoji: "🖋️" }
                                    ].map((opt) => (
                                        <div
                                            key={opt.label}
                                            onClick={() => setOccupation(opt.label)}
                                            className={`p-6 rounded-2xl border-2 transition-all duration-200 cursor-pointer flex flex-col items-center ${occupation === opt.label ? "bg-[#F0F7F4] border-[#5E8B7E]" : "bg-white border-transparent shadow-[0_4px_20px_rgba(0,0,0,0.06)]"
                                                }`}
                                        >
                                            <span className="text-3xl mb-3">{opt.emoji}</span>
                                            <span className="text-[#0F1A2E] text-[15px] font-medium">{opt.label}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {step === 3 && (
                            <div className="text-center">
                                <h1 className="font-serif text-[30px] text-[#0F1A2E] leading-tight font-bold">How familiar are you with investing?</h1>
                                <p className="text-[#6B7A8D] text-[15px] mt-2 mb-10">Be honest — there's no wrong answer</p>

                                <div className="space-y-4">
                                    {[
                                        {
                                            id: "beginner",
                                            title: "New to Investing",
                                            desc: "I've never invested before and want to start from scratch",
                                            emoji: "🌱"
                                        },
                                        {
                                            id: "intermediate",
                                            title: "Know the Basics",
                                            desc: "I understand SIPs, mutual funds and basic stock concepts",
                                            emoji: "📚"
                                        },
                                        {
                                            id: "expert",
                                            title: "Already Investing",
                                            desc: "I actively manage a portfolio and want deeper analysis tools",
                                            emoji: "📈"
                                        }
                                    ].map((opt) => (
                                        <div
                                            key={opt.id}
                                            onClick={() => setExperienceLevel(opt.id)}
                                            className={`flex items-center p-5 rounded-2xl border-2 transition-all duration-200 cursor-pointer text-left ${experienceLevel === opt.id ? "bg-[#F0F7F4] border-[#5E8B7E]" : "bg-white border-transparent shadow-[0_8px_40px_rgba(0,0,0,0.08)]"
                                                }`}
                                        >
                                            <span className="text-4xl mr-4">{opt.emoji}</span>
                                            <div>
                                                <h3 className="text-[#0F1A2E] text-[16px] font-semibold">{opt.title}</h3>
                                                <p className="text-[#6B7A8D] text-[13px] mt-1 pr-4">{opt.desc}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </motion.div>
                </AnimatePresence>

                {/* Nav Buttons */}
                <div className="mt-10 mb-12 flex justify-between items-center h-12">
                    {step > 0 ? (
                        <button
                            onClick={handleBack}
                            className="flex items-center gap-1 text-[#6B7A8D] hover:text-[#5E8B7E] transition-colors text-[14px] font-medium"
                        >
                            <ChevronLeft size={18} />
                            Back
                        </button>
                    ) : <div />}

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate("/features")}
                            className="text-[#6B7A8D] hover:text-[#5E8B7E] transition-colors text-[14px] font-medium"
                        >
                            Skip
                        </button>
                        <button
                            onClick={handleNext}
                            disabled={isNextDisabled() || loading}
                            className={`bg-[#5E8B7E] text-white px-8 py-3 rounded-full text-[15px] font-medium flex items-center gap-1 transition-all duration-300 shadow-lg shadow-[#5E8B7E]/25 ${isNextDisabled() || loading ? "opacity-50 cursor-not-allowed" : "hover:bg-[#4A7A6D] hover:-translate-y-0.5"
                                }`}
                        >
                            {loading ? "Saving..." : step === 3 ? "Let's Go →" : (
                                <>
                                    Continue
                                    <ChevronRight size={18} />
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </main>

            <style>{`
                .no-scrollbar::-webkit-scrollbar { display: none; }
                .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
            `}</style>
        </div>
    );
}
