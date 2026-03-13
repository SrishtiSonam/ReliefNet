// ─── src/models/Simulation.js ─────────────────────────────────────────────────
const { Schema, model } = require("mongoose");
const SimSchema = new Schema({
  name:       String,
  case_study: String,
  districts:  [String],
  methods:    [String],
  n_periods:  Number,
  status:     { type: String, default: "pending" },
  results:    [Schema.Types.Mixed],
  created_at: { type: Date, default: Date.now }
});
module.exports = model("Simulation", SimSchema);
