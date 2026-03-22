import { useState, useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "motion/react"
import { Send, Loader2 } from "lucide-react"
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend, LineChart, Line, XAxis, YAxis } from "recharts"
import { useAuthStore } from "../lib/store/authStore"
import axios from "axios"

const PIE_COLORS = [
  "#5E8B7E", "#4F6D8A", "#D6B97B", "#DFA6A0",
  "#7BA7A0", "#8FA3B8", "#E8D5A3", "#C4897F",
  "#6B9E95", "#5C7FA8"
]

export default function CreatePortfolioPage() {
  const [messages, setMessages] = useState<{role: "user" | "assistant", content: string}[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [allocationJson, setAllocationJson] = useState<any>(null)
  const [approving, setApproving] = useState(false)
  const [backtestResults, setBacktestResults] = useState<any>(null)
  const [backtestLoading, setBacktestLoading] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const navigate = useNavigate()
  const { token, user } = useAuthStore()

  const API = import.meta.env.VITE_AI_URL || "http://localhost:8080"
  const BACKEND = import.meta.env.VITE_API_URL || "http://localhost:4000"

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  useEffect(() => {
    sendMessage("[SESSION START]")
  }, [])

  const sendMessage = async (text: string) => {
    if (text !== "[SESSION START]") {
      setMessages(prev => [...prev, { role: "user", content: text }])
    }
    
    setInput("")
    setLoading(true)
    
    try {
      const res = await axios.post(
        `${API}/advisor/message`,
        {
          session_id: user?.id || "guest",
          user_message: text,
          existing_profile: {},
          conversation_history: messages,
        }
      )
      
      const data = res.data
      
      if (data.response) {
        setMessages(prev => [...prev, { role: "assistant", content: data.response }])
      }
      
      if (data.allocation_json) {
        setAllocationJson(data.allocation_json)
        if (data.backtest_results) {
          setBacktestResults(data.backtest_results)
        }
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, I ran into an issue. Please try again."
      }])
    } finally {
      setLoading(false)
    }
  }

  const runBacktest = async (allocation: any) => {
    setBacktestLoading(true)
    try {
      const res = await axios.post(
        `${API}/backtest`,
        { allocation, years: 5 }
      )
      if (res.data.success) {
        setBacktestResults(res.data.results)
      }
    } catch (err) {
      console.error("Backtest failed:", err)
    } finally {
      setBacktestLoading(false)
    }
  }

  const approvePortfolio = async () => {
    setApproving(true)
    try {
      await axios.post(
        `${BACKEND}/portfolio/create`,
        { 
          allocation: allocationJson,
          backtest_results: backtestResults 
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      navigate("/dashboard")
    } catch (err) {
      console.error("Failed to save portfolio")
    } finally {
      setApproving(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if (input.trim() && !loading && !allocationJson) {
        sendMessage(input.trim())
      }
    }
  }

  return (
    <div className="flex flex-col h-screen bg-[#F7F6F2]">
      {/* NAVBAR */}
      <div className="h-16 bg-white/80 backdrop-blur-md border-b border-black/6 px-6 flex items-center justify-between fixed top-0 w-full z-50">
        <div className="flex items-center gap-2">
          <svg width="22" height="22" viewBox="0 0 36 36" fill="none">
            <ellipse cx="18" cy="19.5" rx="9.5" ry="8" fill="#5E8B7E" opacity="0.96"/>
            <path d="M18 12 L18 27.5" stroke="rgba(0,0,0,0.13)" strokeWidth="0.9" strokeLinecap="round"/>
            <path d="M10.5 17 L25.5 17" stroke="rgba(0,0,0,0.13)" strokeWidth="0.9" strokeLinecap="round"/>
            <ellipse cx="18" cy="8.2" rx="3" ry="2.5" fill="#5E8B7E" opacity="0.96"/>
            <rect x="16.3" y="10.2" width="3.4" height="2.2" rx="1.2" fill="#5E8B7E"/>
            <ellipse cx="6.5" cy="15" rx="3" ry="1.7" transform="rotate(-35 6.5 15)" fill="#5E8B7E" opacity="0.88"/>
            <ellipse cx="29.5" cy="15" rx="3" ry="1.7" transform="rotate(35 29.5 15)" fill="#5E8B7E" opacity="0.88"/>
            <ellipse cx="7.5" cy="24.5" rx="2.5" ry="1.6" transform="rotate(35 7.5 24.5)" fill="#5E8B7E" opacity="0.88"/>
            <ellipse cx="28.5" cy="24.5" rx="2.5" ry="1.6" transform="rotate(-35 28.5 24.5)" fill="#5E8B7E" opacity="0.88"/>
            <ellipse cx="18" cy="28.5" rx="1.3" ry="2" fill="#5E8B7E" opacity="0.75"/>
          </svg>
          <span className="font-serif font-bold text-[1.3rem]">
            <span className="text-[#0F1A2E]">Fin</span>
            <span className="text-[#5E8B7E]">tur</span>
          </span>
        </div>
        <div className="font-sans text-[14px] text-[#6B7A8D]">
          Fund Portfolio Builder
        </div>
        <div className="font-sans text-[12px] text-[#6B7A8D] italic">
          Powered by Arjun
        </div>
      </div>

      {/* CHAT AREA */}
      <div className="flex-1 overflow-y-auto pt-20 pb-4 px-4 md:px-8 max-w-3xl mx-auto w-full">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={msg.role === "user" ? "flex justify-end mb-3" : "flex justify-start mb-3 gap-3"}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-full bg-[#5E8B7E]/10 flex items-center justify-center flex-shrink-0">
                  <svg width="16" height="16" viewBox="0 0 36 36" fill="none">
                    <ellipse cx="18" cy="19.5" rx="9.5" ry="8" fill="#5E8B7E" opacity="0.96"/>
                    <path d="M18 12 L18 27.5" stroke="rgba(0,0,0,0.13)" strokeWidth="0.9" strokeLinecap="round"/>
                    <path d="M10.5 17 L25.5 17" stroke="rgba(0,0,0,0.13)" strokeWidth="0.9" strokeLinecap="round"/>
                    <ellipse cx="18" cy="8.2" rx="3" ry="2.5" fill="#5E8B7E" opacity="0.96"/>
                    <rect x="16.3" y="10.2" width="3.4" height="2.2" rx="1.2" fill="#5E8B7E"/>
                    <ellipse cx="6.5" cy="15" rx="3" ry="1.7" transform="rotate(-35 6.5 15)" fill="#5E8B7E" opacity="0.88"/>
                    <ellipse cx="29.5" cy="15" rx="3" ry="1.7" transform="rotate(35 29.5 15)" fill="#5E8B7E" opacity="0.88"/>
                    <ellipse cx="7.5" cy="24.5" rx="2.5" ry="1.6" transform="rotate(35 7.5 24.5)" fill="#5E8B7E" opacity="0.88"/>
                    <ellipse cx="28.5" cy="24.5" rx="2.5" ry="1.6" transform="rotate(-35 28.5 24.5)" fill="#5E8B7E" opacity="0.88"/>
                    <ellipse cx="18" cy="28.5" rx="1.3" ry="2" fill="#5E8B7E" opacity="0.75"/>
                  </svg>
                </div>
              )}
              
              <div
                className={
                  msg.role === "user"
                    ? "bg-[#5E8B7E] text-white px-4 py-3 rounded-2xl rounded-tr-sm max-w-[75%] font-sans text-[14px] leading-relaxed"
                    : "bg-white text-[#0F1A2E] px-4 py-3 rounded-2xl rounded-tl-sm max-w-[75%] font-sans text-[14px] leading-relaxed shadow-[0_2px_12px_rgba(0,0,0,0.06)] whitespace-pre-wrap"
                }
              >
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <div className="flex justify-start mb-3 gap-3">
            <div className="w-8 h-8 rounded-full bg-[#5E8B7E]/10 flex items-center justify-center flex-shrink-0">
              <svg width="16" height="16" viewBox="0 0 36 36" fill="none">
                <ellipse cx="18" cy="19.5" rx="9.5" ry="8" fill="#5E8B7E" opacity="0.96"/>
                <path d="M18 12 L18 27.5" stroke="rgba(0,0,0,0.13)" strokeWidth="0.9" strokeLinecap="round"/>
                <path d="M10.5 17 L25.5 17" stroke="rgba(0,0,0,0.13)" strokeWidth="0.9" strokeLinecap="round"/>
                <ellipse cx="18" cy="8.2" rx="3" ry="2.5" fill="#5E8B7E" opacity="0.96"/>
                <rect x="16.3" y="10.2" width="3.4" height="2.2" rx="1.2" fill="#5E8B7E"/>
                <ellipse cx="6.5" cy="15" rx="3" ry="1.7" transform="rotate(-35 6.5 15)" fill="#5E8B7E" opacity="0.88"/>
                <ellipse cx="29.5" cy="15" rx="3" ry="1.7" transform="rotate(35 29.5 15)" fill="#5E8B7E" opacity="0.88"/>
                <ellipse cx="7.5" cy="24.5" rx="2.5" ry="1.6" transform="rotate(35 7.5 24.5)" fill="#5E8B7E" opacity="0.88"/>
                <ellipse cx="28.5" cy="24.5" rx="2.5" ry="1.6" transform="rotate(-35 28.5 24.5)" fill="#5E8B7E" opacity="0.88"/>
                <ellipse cx="18" cy="28.5" rx="1.3" ry="2" fill="#5E8B7E" opacity="0.75"/>
              </svg>
            </div>
            <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-sm shadow-[0_2px_12px_rgba(0,0,0,0.06)] flex gap-1 items-center">
              <motion.div className="w-2 h-2 rounded-full bg-[#5E8B7E]/40" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} />
              <motion.div className="w-2 h-2 rounded-full bg-[#5E8B7E]/40" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.15 }} />
              <motion.div className="w-2 h-2 rounded-full bg-[#5E8B7E]/40" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.3 }} />
            </div>
          </div>
        )}
        
        {/* ALLOCATION CARD */}
        {allocationJson !== null && (
          <div className="mx-4 md:mx-8 mb-4 max-w-3xl mx-auto w-full bg-white rounded-2xl p-6 shadow-[0_8px_40px_rgba(0,0,0,0.08)] border border-[rgba(94,139,126,0.2)] mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="font-serif text-[18px] text-[#0F1A2E]">Your Portfolio Allocation</h2>
              <div className="bg-[#5E8B7E]/10 text-[#5E8B7E] font-sans text-[12px] px-3 py-1 rounded-full">
                Ready to Approve
              </div>
            </div>
            
            <div className="flex flex-col md:flex-row gap-8 items-center">
              {/* LEFT - Pie Chart */}
              <div className="w-full md:w-1/2">
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={Object.entries(allocationJson.allocation || allocationJson).map(([name, val]: any) => ({ name, value: val.percentage }))}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {Object.entries(allocationJson.allocation || allocationJson).map((_, index) => (
                        <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontFamily: "DM Sans", fontSize: "12px" }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* RIGHT - Allocation List */}
              <div className="w-full md:w-1/2 flex flex-col">
                {Object.entries(allocationJson.allocation || allocationJson).map(([name, val]: any, index) => (
                  <div key={name} className="flex justify-between items-center py-2 border-b border-black/4 last:border-0 relative">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }} />
                      <span className="font-sans text-[14px] text-[#0F1A2E]">{name}</span>
                    </div>
                    <span className="font-sans text-[14px] font-semibold text-[#5E8B7E]">{val.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* BACKTEST SECTION */}
            {backtestResults && (() => {
              const s = backtestResults.summary
              const invested = s?.total_invested || 0
              const finalVal = s?.final_portfolio_value || 0
              const gains = s?.total_gains || 0
              const xirr = s?.xirr_pct || 0
              const absReturn = s?.absolute_return_pct || 0

              const donutData = [
                { name: "Invested", value: invested },
                { name: "Est. Returns", value: gains > 0 ? gains : 0 },
              ]
              const DONUT_COLORS = ["#E8EDF2", "#5E8B7E"]

              const holdings = backtestResults.final_holdings || {}

              return (
                <div className="mt-6 pt-6 border-t border-black/6">
                  
                  <h3 className="font-serif text-[16px] text-[#0F1A2E] mb-6">
                    5-Year Backtest Projection
                  </h3>

                  {/* MAIN ROW: inputs left, donut right */}
                  <div className="flex flex-col md:flex-row gap-6 items-center mb-6">
                    
                    {/* LEFT — Key Stats */}
                    <div className="flex flex-col gap-4 w-full md:w-1/2">
                      
                      {/* Monthly SIP */}
                      <div className="flex items-center justify-between bg-[#F7F6F2] rounded-xl px-4 py-3">
                        <span className="font-sans text-[13px] text-[#6B7A8D]">Monthly SIP</span>
                        <span className="font-sans text-[15px] font-bold text-[#0F1A2E]">
                          ₹{s?.monthly_sip?.toLocaleString("en-IN")}
                        </span>
                      </div>

                      {/* XIRR */}
                      <div className="flex items-center justify-between bg-[#F0F7F4] rounded-xl px-4 py-3">
                        <span className="font-sans text-[13px] text-[#6B7A8D]">XIRR</span>
                        <span className="font-sans text-[15px] font-bold text-[#5E8B7E]">
                          {xirr}%
                        </span>
                      </div>

                      {/* Period */}
                      <div className="flex items-center justify-between bg-[#F7F6F2] rounded-xl px-4 py-3">
                        <span className="font-sans text-[13px] text-[#6B7A8D]">Period</span>
                        <span className="font-sans text-[15px] font-bold text-[#0F1A2E]">
                          5 Years
                        </span>
                      </div>

                      {/* Absolute Return */}
                      <div className="flex items-center justify-between bg-[#F0F7F4] rounded-xl px-4 py-3">
                        <span className="font-sans text-[13px] text-[#6B7A8D]">Absolute Return</span>
                        <span className="font-sans text-[15px] font-bold text-[#5E8B7E]">
                          {absReturn}%
                        </span>
                      </div>
                    </div>

                    {/* RIGHT — Donut Chart */}
                    <div className="w-full md:w-1/2 flex flex-col items-center">
                      <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                          <Pie
                            data={donutData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={90}
                            paddingAngle={2}
                            dataKey="value"
                            startAngle={90}
                            endAngle={-270}
                          >
                            {donutData.map((_, i) => (
                              <Cell key={i} fill={DONUT_COLORS[i]} />
                            ))}
                          </Pie>
                          <Tooltip
                            formatter={(v: any) => `₹${Number(v).toLocaleString("en-IN")}`}
                          />
                        </PieChart>
                      </ResponsiveContainer>

                      {/* Legend */}
                      <div className="flex gap-4 mt-2">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-[#E8EDF2]"/>
                          <span className="font-sans text-[12px] text-[#6B7A8D]">Invested amount</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-[#5E8B7E]"/>
                          <span className="font-sans text-[12px] text-[#6B7A8D]">Est. returns</span>
                        </div>
                      </div>

                      {/* Three numbers below chart */}
                      <div className="mt-4 w-full flex flex-col gap-2">
                        <div className="flex justify-between px-4 py-2 rounded-xl bg-[#F7F6F2]">
                          <span className="font-sans text-[13px] text-[#6B7A8D]">Total Invested</span>
                          <span className="font-sans text-[14px] font-semibold text-[#0F1A2E]">
                            ₹{invested.toLocaleString("en-IN")}
                          </span>
                        </div>
                        <div className="flex justify-between px-4 py-2 rounded-xl bg-[#F7F6F2]">
                          <span className="font-sans text-[13px] text-[#6B7A8D]">Est. Returns</span>
                          <span className="font-sans text-[14px] font-semibold text-[#5E8B7E]">
                            ₹{gains.toLocaleString("en-IN")}
                          </span>
                        </div>
                        <div className="flex justify-between px-4 py-2 rounded-xl bg-[#F0F7F4]">
                          <span className="font-sans text-[13px] font-medium text-[#0F1A2E]">
                            Final Value
                          </span>
                          <span className="font-sans text-[14px] font-bold text-[#5E8B7E]">
                            ₹{finalVal.toLocaleString("en-IN")}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* ETF Holdings */}
                  {Object.keys(holdings).length > 0 && (
                    <div className="mb-2">
                      <p className="font-sans text-[13px] text-[#6B7A8D] mb-2">
                        Selected ETFs
                      </p>
                      <div className="rounded-xl overflow-hidden border border-black/6">
                        {Object.entries(holdings).map(([ac, h]: any, i) => (
                          <div key={ac} className={`flex justify-between items-center px-4 py-3 font-sans text-[13px] ${i % 2 === 0 ? "bg-white" : "bg-[#F7F6F2]"}`}>
                            <div className="flex flex-col">
                              <span className="text-[#0F1A2E] font-medium">{ac}</span>
                              <span className="text-[#6B7A8D] text-[11px]">{h.name}</span>
                            </div>
                            <div className="flex flex-col items-end">
                              <span className="text-[#5E8B7E] font-semibold">
                                {h.ticker}
                              </span>
                              <span className="text-[#6B7A8D] text-[11px]">
                                ₹{h.current_value?.toLocaleString("en-IN")}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                </div>
              )
            })()}

            <div className="flex flex-col gap-3 mt-6">
              <button
                onClick={approvePortfolio}
                disabled={approving || (backtestResults === null)}
                className="w-full h-14 rounded-full bg-[#5E8B7E] text-white font-serif text-[16px] hover:bg-[#4A7A6D] hover:-translate-y-0.5 transition-all shadow-lg shadow-[#5E8B7E]/30 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {approving ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Saving...
                  </>
                ) : (
                  "Approve & Save Portfolio →"
                )}
              </button>

              <button
                onClick={() => {
                  setAllocationJson(null)
                  setBacktestResults(null)
                  setMessages(prev => [...prev, {
                    role: "assistant",
                    content: "No problem! Let's refine your plan. What would you like to change?"
                  }])
                }}
                className="w-full h-12 rounded-full border-2 border-[#6B7A8D]/30 text-[#6B7A8D] font-sans text-[14px] hover:border-[#5E8B7E] hover:text-[#5E8B7E] transition-all"
              >
                Not quite right — continue chatting
              </button>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* INPUT BAR */}
      <div className="bg-white/90 backdrop-blur-md border-t border-black/6 px-4 py-3 fixed bottom-0 w-full z-50">
        <div className="max-w-3xl mx-auto flex gap-3 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={allocationJson !== null}
            placeholder={allocationJson !== null ? "Portfolio generated. Ready to approve." : "Type your message..."}
            rows={1}
            className="flex-1 min-h-[48px] max-h-[120px] bg-[#F7F6F2] rounded-2xl px-4 py-3 font-sans text-[14px] text-[#0F1A2E] resize-none border border-black/8 focus:outline-none focus:border-[#5E8B7E] focus:ring-2 focus:ring-[#5E8B7E]/10 disabled:opacity-50"
            style={{
              height: "auto",
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement
              target.style.height = "auto"
              target.style.height = target.scrollHeight + "px"
            }}
          />
          <button
            onClick={() => {
              if (input.trim() && !loading && !allocationJson) {
                sendMessage(input.trim())
              }
            }}
            disabled={loading || !input.trim() || allocationJson !== null}
            className="w-12 h-12 rounded-full bg-[#5E8B7E] flex items-center justify-center flex-shrink-0 hover:bg-[#4A7A6D] hover:scale-105 transition-all disabled:opacity-40 disabled:hover:scale-100"
          >
            {loading ? <Loader2 className="w-5 h-5 text-white animate-spin" /> : <Send className="w-5 h-5 text-white" />}
          </button>
        </div>
      </div>
      {/* PADDING FOR FIXED INPUT BAR */}
      <div className="h-[72px]" />
    </div>
  )
}
