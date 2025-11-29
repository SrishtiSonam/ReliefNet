import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function ResourceMap() {
    // Dummy data for Indian districts with resources
    const [districts] = useState([
        {
            id: 1,
            name: 'Mumbai',
            position: [19.0760, 72.8777],
            resources: { ambulances: 15, trucks: 8, drones: 3 },
            activeCases: 2,
            severity: 'medium'
        },
        {
            id: 2,
            name: 'Delhi',
            position: [28.7041, 77.1025],
            resources: { ambulances: 20, trucks: 12, drones: 5 },
            activeCases: 1,
            severity: 'low'
        },
        {
            id: 3,
            name: 'Bangalore',
            position: [12.9716, 77.5946],
            resources: { ambulances: 12, trucks: 7, drones: 2 },
            activeCases: 0,
            severity: 'none'
        },
        {
            id: 4,
            name: 'Chennai',
            position: [13.0827, 80.2707],
            resources: { ambulances: 10, trucks: 6, drones: 2 },
            activeCases: 3,
            severity: 'high'
        },
        {
            id: 5,
            name: 'Kolkata',
            position: [22.5726, 88.3639],
            resources: { ambulances: 14, trucks: 9, drones: 4 },
            activeCases: 1,
            severity: 'medium'
        },
        {
            id: 6,
            name: 'Hyderabad',
            position: [17.3850, 78.4867],
            resources: { ambulances: 11, trucks: 7, drones: 3 },
            activeCases: 0,
            severity: 'none'
        },
        {
            id: 7,
            name: 'Pune',
            position: [18.5204, 73.8567],
            resources: { ambulances: 8, trucks: 5, drones: 2 },
            activeCases: 1,
            severity: 'low'
        }
    ]);

    const [selectedDistrict, setSelectedDistrict] = useState(null);

    const getSeverityColor = (severity) => {
        const colors = {
            none: '#10b981',
            low: '#3b82f6',
            medium: '#f59e0b',
            high: '#ef4444',
            critical: '#991b1b'
        };
        return colors[severity] || '#6b7280';
    };

    const getSeverityRadius = (severity) => {
        const radii = {
            none: 15000,
            low: 25000,
            medium: 35000,
            high: 50000,
            critical: 75000
        };
        return radii[severity] || 20000;
    };

    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">Resource Distribution Map</h2>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Map */}
                <div className="lg:col-span-2 card p-0 overflow-hidden" style={{ height: '600px' }}>
                    <MapContainer
                        center={[20.5937, 78.9629]}
                        zoom={5}
                        style={{ height: '100%', width: '100%' }}
                    >
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />

                        {districts.map((district) => (
                            <React.Fragment key={district.id}>
                                <Circle
                                    center={district.position}
                                    radius={getSeverityRadius(district.severity)}
                                    pathOptions={{
                                        color: getSeverityColor(district.severity),
                                        fillColor: getSeverityColor(district.severity),
                                        fillOpacity: 0.2
                                    }}
                                />
                                <Marker
                                    position={district.position}
                                    eventHandlers={{
                                        click: () => setSelectedDistrict(district)
                                    }}
                                >
                                    <Popup>
                                        <div className="p-2">
                                            <h3 className="font-bold text-lg">{district.name}</h3>
                                            <div className="mt-2 space-y-1 text-sm">
                                                <p><strong>Active Cases:</strong> {district.activeCases}</p>
                                                <p><strong>Severity:</strong> <span className="capitalize">{district.severity}</span></p>
                                                <hr className="my-2" />
                                                <p><strong>Resources Available:</strong></p>
                                                <p>🚑 Ambulances: {district.resources.ambulances}</p>
                                                <p>🚛 Trucks: {district.resources.trucks}</p>
                                                <p>🚁 Drones: {district.resources.drones}</p>
                                            </div>
                                        </div>
                                    </Popup>
                                </Marker>
                            </React.Fragment>
                        ))}
                    </MapContainer>
                </div>

                {/* District Info Panel */}
                <div className="space-y-4">
                    <div className="card">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">District Information</h3>
                        {selectedDistrict ? (
                            <div className="space-y-3">
                                <div>
                                    <h4 className="text-xl font-bold text-primary-600">{selectedDistrict.name}</h4>
                                    <p className="text-sm text-gray-500">Click markers on map for details</p>
                                </div>

                                <div className="border-t border-gray-200 pt-3">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-sm font-medium text-gray-700">Severity:</span>
                                        <span
                                            className="px-2 py-1 text-xs font-medium rounded capitalize"
                                            style={{
                                                backgroundColor: getSeverityColor(selectedDistrict.severity) + '20',
                                                color: getSeverityColor(selectedDistrict.severity)
                                            }}
                                        >
                                            {selectedDistrict.severity}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm font-medium text-gray-700">Active Cases:</span>
                                        <span className="text-lg font-bold">{selectedDistrict.activeCases}</span>
                                    </div>
                                </div>

                                <div className="border-t border-gray-200 pt-3">
                                    <p className="text-sm font-medium text-gray-700 mb-2">Available Resources:</p>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <span className="text-sm">🚑 Ambulances</span>
                                            <span className="font-semibold">{selectedDistrict.resources.ambulances}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">🚛 Trucks</span>
                                            <span className="font-semibold">{selectedDistrict.resources.trucks}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">🚁 Drones</span>
                                            <span className="font-semibold">{selectedDistrict.resources.drones}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <p className="text-3xl mb-2">🗺️</p>
                                <p className="text-sm">Click on a district marker to view details</p>
                            </div>
                        )}
                    </div>

                    {/* Legend */}
                    <div className="card">
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">Severity Legend</h3>
                        <div className="space-y-2">
                            {['none', 'low', 'medium', 'high', 'critical'].map((severity) => (
                                <div key={severity} className="flex items-center">
                                    <div
                                        className="w-4 h-4 rounded-full mr-2"
                                        style={{ backgroundColor: getSeverityColor(severity) }}
                                    ></div>
                                    <span className="text-sm capitalize">{severity}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ResourceMap;
