const mongoose = require('mongoose');

const WarehouseSchema = new mongoose.Schema({
    name: { type: String, required: true },
    district_name: { type: String, required: true },
    lat: { type: Number, required: true },
    lng: { type: Number, required: true },
    inventory: {
        food_kits: { type: Number, default: 0 },
        water_liters: { type: Number, default: 0 },
        medical_kits: { type: Number, default: 0 },
        tents: { type: Number, default: 0 }
    },
    capacity: { type: Number, default: 10000 },
    type: { type: String, enum: ['State Capital', 'Post Office', 'Temporary Camp'], default: 'Temporary Camp' }
}, {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

module.exports = mongoose.model('Warehouse', WarehouseSchema, 'warehouses');
