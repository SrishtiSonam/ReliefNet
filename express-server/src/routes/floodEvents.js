// ─── src/routes/floodEvents.js ────────────────────────────────────────────────
const router  = require("express").Router();
const axios   = require("axios");
const FASTAPI = process.env.FASTAPI_URL || "http://localhost:8000";

router.get("/",           async (req, res) => {
  const { data } = await axios.get(`${FASTAPI}/api/flood-events/`, { params: req.query });
  res.json(data);
});

router.get("/kerala-2018", async (req, res) => {
  const { data } = await axios.get(`${FASTAPI}/api/flood-events/kerala-2018`);
  res.json(data);
});

router.get("/inventory",  async (req, res) => {
  const { data } = await axios.get(`${FASTAPI}/api/flood-events/inventory`, { params: req.query });
  res.json(data);
});

module.exports = router;