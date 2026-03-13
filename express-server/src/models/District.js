// ─── src/models/District.js ───────────────────────────────────────────────────
const { Schema, model } = require("mongoose");
const DistSchema = new Schema({
  dist_name:    String,
  state_name:   String,
  latitude:     Number,
  longitude:    Number,
  dfsi_score:   Number,
  demand_mean:  Number,
  truck_cost:   Number,
  uav_cost:     Number,
  population:   Number,
});
module.exports = model("District", DistSchema);
