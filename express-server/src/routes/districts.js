// ─── src/routes/districts.js ──────────────────────────────────────────────────
const router  = require("express").Router();
const axios   = require("axios");
const FASTAPI = process.env.FASTAPI_URL || "http://localhost:8000";

router.get("/", async (req, res) => {
  const { data } = await axios.get(`${FASTAPI}/api/districts/`);
  res.json(data);
});

router.get("/dfsi", async (req, res) => {
  const { data } = await axios.get(`${FASTAPI}/api/districts/dfsi/all`);
  res.json(data);
});

router.get("/:name/demand", async (req, res) => {
  const { data } = await axios.get(
    `${FASTAPI}/api/districts/${req.params.name}/demand`,
    { params: req.query }
  );
  res.json(data);
});

module.exports = router;
