require("dotenv").config();
const express = require("express");
const cors = require("cors");
const passport = require("./config/passport");

const app = express();

app.use(cors({
    origin: process.env.FRONTEND_URL || "http://localhost:5173",
    credentials: true,
}));

app.use(express.json());
app.use(passport.initialize());

app.use("/auth", require("./routes/auth.routes"));
const aiRoutes = require("./routes/ai.routes");
app.use("/api/ai", aiRoutes);
app.use("/portfolio", require("./routes/portfolio.routes"));

app.get("/health", (req, res) => {
    res.json({ status: "Fintur backend running" });
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
    console.log(`Backend running on port ${PORT}`);
});
