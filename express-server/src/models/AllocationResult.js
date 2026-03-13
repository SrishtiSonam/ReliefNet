// ─── src/models/AllocationResult.js ──────────────────────────────────────────
const { Schema, model } = require("mongoose");
const ResultSchema = new Schema({
  simulation_id:        String,
  method:               String,
  total_cost:           Number,
  deprivation_cost:     Number,
  transport_cost:       Number,
  max_deprivation_time: Number,
  demand_coverage:      Number,
  decisions:            [Schema.Types.Mixed],
  created_at:           { type: Date, default: Date.now }
});
module.exports = model("AllocationResult", ResultSchema);
