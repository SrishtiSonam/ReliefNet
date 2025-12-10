import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapView = ({ simulationData, center = [20.5937, 78.9629], zoom = 5, markers = [], vehicles = [], districts: propDistricts = [] }) => {
    const mapRef = useRef(null);
    const mapInstanceRef = useRef(null);
    const [districts, setDistricts] = useState([]);
    const [routes, setRoutes] = useState([]);
    const markersRef = useRef([]);
    const vehicleMarkersRef = useRef([]);
    const customMarkersRef = useRef([]);

    // Load initial districts (Mock data for simulation mode)
    useEffect(() => {
        if (!simulationData && propDistricts.length === 0) {
            const mockDistricts = [
                { id: 0, name: 'New Delhi', lat: 28.6139, lon: 77.2090, demand: 150, vulnerability: 0.8 },
                { id: 1, name: 'Mumbai', lat: 19.0760, lon: 72.8777, demand: 80, vulnerability: 0.5 },
                { id: 2, name: 'Chennai', lat: 13.0827, lon: 80.2707, demand: 200, vulnerability: 0.9 },
                { id: 3, name: 'Kolkata', lat: 22.5726, lon: 88.3639, demand: 120, vulnerability: 0.6 },
                { id: 4, name: 'Bangalore', lat: 12.9716, lon: 77.5946, demand: 90, vulnerability: 0.4 },
            ];
            setDistricts(mockDistricts);

            const mockRoutes = [
                { from: [28.6139, 77.2090], to: [19.0760, 72.8777], type: 'truck', status: 'active' },
                { from: [13.0827, 80.2707], to: [12.9716, 77.5946], type: 'uav', status: 'active' },
            ];
            setRoutes(mockRoutes);
        }
    }, [simulationData, propDistricts]);

    // Update districts when simulation data changes
    useEffect(() => {
        if (simulationData && simulationData.demand) {
            const updatedDistricts = districts.map(d => ({
                ...d,
                demand: simulationData.demand[d.id] || d.demand
            }));
            setDistricts(updatedDistricts);
        }
    }, [simulationData]);

    // Update map view when center or zoom changes
    useEffect(() => {
        if (mapInstanceRef.current) {
            mapInstanceRef.current.setView(center, zoom);
        }
    }, [center, zoom]);

    useEffect(() => {
        if (!mapRef.current || mapInstanceRef.current) return;

        // Initialize map centered on provided center or India
        const map = L.map(mapRef.current).setView(center, zoom);
        mapInstanceRef.current = map;

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18,
        }).addTo(map);

        // Add depot marker (central warehouse) - Nagpur (Central India)
        const depotIcon = L.divIcon({
            className: 'custom-depot-icon',
            html: '<div style="background: #3b82f6; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">🏭</div>',
            iconSize: [30, 30],
        });
        L.marker([21.1458, 79.0882], { icon: depotIcon })
            .addTo(map)
            .bindPopup('<b>Central Depot (Nagpur)</b><br>Main Supply Hub');

        return () => {
            if (mapInstanceRef.current) {
                mapInstanceRef.current.remove();
                mapInstanceRef.current = null;
            }
        };
    }, []);

    // Update districts on map (Simulation Mode)
    useEffect(() => {
        if (!mapInstanceRef.current || districts.length === 0) return;

        const map = mapInstanceRef.current;

        // Clear old markers
        markersRef.current.forEach(marker => map.removeLayer(marker));
        markersRef.current = [];

        districts.forEach(district => {
            // Color based on demand level
            const color = district.demand > 150 ? '#ef4444' : district.demand > 100 ? '#f59e0b' : '#10b981';
            const radius = Math.max(district.demand / 10, 10);

            // Add circle for demand visualization
            const circle = L.circle([district.lat, district.lon], {
                color: color,
                fillColor: color,
                fillOpacity: 0.4,
                radius: radius * 100,
            }).addTo(map).bindPopup('<b>' + district.name + '</b><br>Demand: ' + district.demand + ' units<br>Vulnerability: ' + (district.vulnerability * 100).toFixed(0) + '%');
            markersRef.current.push(circle);

            // Add marker
            const markerIcon = L.divIcon({
                className: 'custom-marker',
                html: '<div style="background: ' + color + '; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>',
                iconSize: [20, 20],
            });
            const marker = L.marker([district.lat, district.lon], { icon: markerIcon }).addTo(map);
            markersRef.current.push(marker);
        });
    }, [districts]);

    // Render Custom Markers (from props)
    useEffect(() => {
        if (!mapInstanceRef.current) return;
        const map = mapInstanceRef.current;

        // Clear old custom markers
        customMarkersRef.current.forEach(marker => map.removeLayer(marker));
        customMarkersRef.current = [];

        markers.forEach(markerData => {
            const marker = L.marker([markerData.lat, markerData.lng])
                .addTo(map)
                .bindPopup(`<b>${markerData.name}</b><br>${markerData.description}`);
            customMarkersRef.current.push(marker);
        });
    }, [markers]);

    // Render Vehicles (from props)
    useEffect(() => {
        if (!mapInstanceRef.current) return;
        const map = mapInstanceRef.current;

        // Clear old vehicle markers
        vehicleMarkersRef.current.forEach(marker => map.removeLayer(marker));
        vehicleMarkersRef.current = [];

        vehicles.forEach(vehicle => {
            const color = vehicle.type === 'truck' ? '#3b82f6' : '#10b981';
            const iconHtml = vehicle.type === 'truck' ? '🚛' : '🚁';

            const vehicleIcon = L.divIcon({
                className: 'vehicle-icon',
                html: `<div style="background: ${color}; width: 30px; height: 30px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; font-size: 16px;">${iconHtml}</div>`,
                iconSize: [30, 30],
            });

            const marker = L.marker([vehicle.lat, vehicle.lng], { icon: vehicleIcon })
                .addTo(map)
                .bindPopup(`<b>${vehicle.name}</b><br>Type: ${vehicle.type}<br>Status: ${vehicle.status}`);
            vehicleMarkersRef.current.push(marker);
        });
    }, [vehicles]);

    // Update routes on map
    useEffect(() => {
        if (!mapInstanceRef.current || routes.length === 0) return;

        const map = mapInstanceRef.current;

        routes.forEach(route => {
            const color = route.type === 'truck' ? '#3b82f6' : '#10b981';
            const dashArray = route.type === 'uav' ? '10, 10' : null;

            L.polyline([route.from, route.to], {
                color: color,
                weight: 3,
                opacity: 0.7,
                dashArray: dashArray,
            }).addTo(map).bindPopup('<b>' + (route.type === 'truck' ? 'Truck Route' : 'UAV Path') + '</b><br>Status: ' + route.status);

            // Add arrow at the end
            const arrowIcon = L.divIcon({
                className: 'route-arrow',
                html: '<div style="color: ' + color + '; font-size: 20px;">➤</div>',
                iconSize: [20, 20],
            });
            L.marker(route.to, { icon: arrowIcon }).addTo(map);
        });
    }, [routes]);

    return (
        <div className="flex-grow bg-gray-800 rounded-lg overflow-hidden relative" style={{ height: '600px' }}>
            <div ref={mapRef} style={{ width: '100%', height: '100%' }}></div>

            {/* Legend */}
            <div className="absolute bottom-4 right-4 bg-gray-900 bg-opacity-90 p-4 rounded-lg text-sm z-[1000]">
                <h3 className="font-bold mb-2">Legend</h3>
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-red-500"></div>
                        <span>High Demand (&gt;150)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                        <span>Medium Demand (100-150)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-green-500"></div>
                        <span>Low Demand (&lt;100)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-1 bg-blue-500"></div>
                        <span>Truck Route</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-1 bg-green-500 border-dashed border-t-2"></div>
                        <span>UAV Path</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-blue-400">🏭</span>
                        <span>Central Depot</span>
                    </div>
                </div>
            </div>

            {/* Live indicator */}
            {simulationData && (
                <div className="absolute top-4 right-4 bg-green-600 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2 z-[1000]">
                    <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                    LIVE - Step {simulationData.step}
                </div>
            )}
        </div>
    );
};

export default MapView;
