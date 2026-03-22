const express = require("express");
const router = express.Router();
const authMiddleware = require("../middleware/authMiddleware");
const portfolioController = require("../controllers/portfolio.controller");

router.post("/create", authMiddleware, 
  portfolioController.createPortfolio);

module.exports = router;
