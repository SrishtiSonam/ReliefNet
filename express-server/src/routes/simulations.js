// ─── src/routes/simulations.js ────────────────────────────────────────────────
const router  = require("express").Router();
const axios   = require("axios");
const Sim     = require("../models/Simulation");
const FASTAPI = process.env.FASTAPI_URL || "http://localhost:8000";

// Trigger simulation via FastAPI ML engine
router.post("/", async (req, res) => {
  try {
    const { data } = await axios.post(`${FASTAPI}/api/simulation/run`, req.body);
    const sim = await Sim.create({ ...req.body, status: "pending" });
    res.json({ express_id: sim._id, fastapi_id: data.simulation_id });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

router.get("/", async (req, res) => {
  const sims = await Sim.find().sort({ created_at: -1 }).limit(50);
  res.json(sims);
});

router.get("/:id/status", async (req, res) => {
  try {
    const { data } = await axios.get(`${FASTAPI}/api/simulation/${req.params.id}`);
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

module.exports = router;
