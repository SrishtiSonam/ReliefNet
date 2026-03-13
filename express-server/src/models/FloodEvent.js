const mongoose = require('mongoose');

const FloodEventSchema = new mongoose.Schema({
  event_name: { type: String, required: true },
  district_name: { type: String, required: true },
  severity: { type: String, enum: ['Low', 'Medium', 'High', 'Critical'], required: true },
  observed_date: { type: Date, required: true },
  affected_population: { type: Number, default: 0 },
  predicted_duration_days: { type: Number, default: 0 },
  water_level_rise_cm: { type: Number, default: 0 }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

module.exports = mongoose.model('FloodEvent', FloodEventSchema, 'flood_events');
