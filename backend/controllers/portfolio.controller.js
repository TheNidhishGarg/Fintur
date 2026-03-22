const portfolioService = 
  require("../services/portfolio.service");

exports.createPortfolio = async (req, res) => {
  try {
    const { allocation, backtest_results } = req.body;
    if (!allocation) {
      return res.status(400).json({ 
        error: "Allocation data is required" 
      });
    }
    const portfolio = await portfolioService
      .savePortfolio(
        req.user.id,
        allocation,
        backtest_results
      );
    res.json({ success: true, portfolio });
  } catch (err) {
    res.status(500).json({ 
      error: "Failed to save portfolio" 
    });
  }
};
