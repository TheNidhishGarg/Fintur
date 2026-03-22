const { createClient } = require("@supabase/supabase-js");

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

exports.savePortfolio = async (
  userId, allocation, backtestResults
) => {
  const { data, error } = await supabase
    .from("portfolios")
    .insert({
      user_id: userId,
      allocation: allocation,
      backtest_results: backtestResults || null,
      status: "approved",
      created_at: new Date().toISOString(),
    })
    .select()
    .single();

  if (error) throw new Error("Failed to save portfolio");
  return data;
};
