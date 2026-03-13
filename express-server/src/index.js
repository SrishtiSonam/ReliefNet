// ─── src/index.js ─────────────────────────────────────────────────────────────
const express  = require("express");
const mongoose = require("mongoose");
const cors     = require("cors");
require("dotenv").config();

const districtRoutes   = require("./routes/districts");
const simulationRoutes = require("./routes/simulations");
const floodRoutes      = require("./routes/floodEvents");
const resultRoutes     = require("./routes/results");

const app = express();
app.use(cors({ origin: "http://localhost:3000" }));
app.use(express.json());

mongoose.connect(process.env.MONGO_URI || "mongodb://localhost:27017/flood_relief_india")
  .then(() => console.log("MongoDB connected"))
  .catch(err => console.error("MongoDB error:", err));

app.use("/api/districts",   districtRoutes);
app.use("/api/simulations", simulationRoutes);
app.use("/api/flood-events",floodRoutes);
app.use("/api/results",     resultRoutes);

app.listen(process.env.PORT || 5000,
  () => console.log(`Express running on port ${process.env.PORT || 5000}`));

  