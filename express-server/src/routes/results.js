// ─── src/routes/results.js ────────────────────────────────────────────────────
const router = require("express").Router();
const Result = require("../models/AllocationResult");

router.get("/:simId", async (req, res) => {
  const results = await Result.find({ simulation_id: req.params.simId });
  res.json(results);
});

router.post("/", async (req, res) => {
  const result = await Result.create(req.body);
  res.json(result);
});

module.exports = router;