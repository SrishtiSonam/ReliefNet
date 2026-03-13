import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

/* Fix default Leaflet icons */
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const MapView = ({
  simulationData,
  center = [20.5937, 78.9629],
  zoom = 5,
  markers = [],
  vehicles = [],
  districts: propDistricts = [],
}) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  const [districts, setDistricts] = useState([]);
  const [routes, setRoutes] = useState([]);

  const markersRef = useRef([]);
  const vehicleMarkersRef = useRef([]);
  const customMarkersRef = useRef([]);
  const routesRef = useRef([]);

  /* Load initial districts */
  useEffect(() => {
    if (!simulationData && propDistricts.length === 0) {
      const mockDistricts = [
        { id: 0, name: "New Delhi", lat: 28.6139, lon: 77.209, demand: 150, vulnerability: 0.8 },
        { id: 1, name: "Mumbai", lat: 19.076, lon: 72.8777, demand: 80, vulnerability: 0.5 },
        { id: 2, name: "Chennai", lat: 13.0827, lon: 80.2707, demand: 200, vulnerability: 0.9 },
        { id: 3, name: "Kolkata", lat: 22.5726, lon: 88.3639, demand: 120, vulnerability: 0.6 },
        { id: 4, name: "Bangalore", lat: 12.9716, lon: 77.5946, demand: 90, vulnerability: 0.4 },
      ];

      setDistricts(mockDistricts);

      const mockRoutes = [
        { from: [28.6139, 77.209], to: [19.076, 72.8777], type: "truck", status: "active" },
        { from: [13.0827, 80.2707], to: [12.9716, 77.5946], type: "uav", status: "active" },
      ];

      setRoutes(mockRoutes);
    }
  }, [simulationData, propDistricts]);

  /* Update districts from simulation */
  useEffect(() => {
    if (simulationData && simulationData.demand) {
      const updated = districts.map((d) => ({
        ...d,
        demand: simulationData.demand[d.id] || d.demand,
      }));
      setDistricts(updated);
    }
  }, [simulationData]);

  /* Initialize map */
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    const map = L.map(mapRef.current).setView(center, zoom);
    mapInstanceRef.current = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
      maxZoom: 18,
    }).addTo(map);

    /* Central Depot */
    const depotIcon = L.divIcon({
      className: "custom-depot-icon",
      html:
        '<div style="background:#3b82f6;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:3px solid white;color:white;">🏭</div>',
      iconSize: [30, 30],
    });

    L.marker([21.1458, 79.0882], { icon: depotIcon })
      .addTo(map)
      .bindPopup("<b>Central Depot (Nagpur)</b><br>Main Supply Hub");

    return () => {
      map.remove();
    };
  }, []);

  /* Render districts */
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    markersRef.current.forEach((m) => map.removeLayer(m));
    markersRef.current = [];

    districts.forEach((district) => {
      let color;

      if (district.demand > 180) color = "#dc2626";
      else if (district.demand > 120) color = "#f59e0b";
      else color = "#10b981";

      const circle = L.circle([district.lat, district.lon], {
        color,
        fillColor: color,
        fillOpacity: 0.4,
        radius: district.demand * 100,
      })
        .addTo(map)
        .bindPopup(
          `<b>${district.name}</b><br>
           Demand: ${district.demand} units<br>
           Vulnerability: ${(district.vulnerability * 100).toFixed(0)}%`
        );

      markersRef.current.push(circle);

      const markerIcon = L.divIcon({
        className: "custom-marker",
        html: `<div style="background:${color};width:20px;height:20px;border-radius:50%;border:2px solid white;"></div>`,
        iconSize: [20, 20],
      });

      const marker = L.marker([district.lat, district.lon], {
        icon: markerIcon,
      }).addTo(map);

      markersRef.current.push(marker);
    });
  }, [districts]);

  /* Render custom markers */
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    customMarkersRef.current.forEach((m) => map.removeLayer(m));
    customMarkersRef.current = [];

    markers.forEach((m) => {
      const marker = L.marker([m.lat, m.lng])
        .addTo(map)
        .bindPopup(`<b>${m.name}</b><br>${m.description}`);
      customMarkersRef.current.push(marker);
    });
  }, [markers]);

  /* Render vehicles */
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    vehicleMarkersRef.current.forEach((m) => map.removeLayer(m));
    vehicleMarkersRef.current = [];

    vehicles.forEach((vehicle) => {
      const color = vehicle.type === "truck" ? "#3b82f6" : "#10b981";
      const iconHtml = vehicle.type === "truck" ? "🚛" : "🚁";

      const icon = L.divIcon({
        className: "vehicle-icon",
        html: `<div style="background:${color};width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid white;">${iconHtml}</div>`,
        iconSize: [30, 30],
      });

      const marker = L.marker([vehicle.lat, vehicle.lng], { icon })
        .addTo(map)
        .bindPopup(
          `<b>${vehicle.name}</b><br>Type: ${vehicle.type}<br>Status: ${vehicle.status}`
        );

      vehicleMarkersRef.current.push(marker);
    });
  }, [vehicles]);

  /* Render routes */
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    routesRef.current.forEach((r) => map.removeLayer(r));
    routesRef.current = [];

    routes.forEach((route) => {
      const color = route.type === "truck" ? "#3b82f6" : "#10b981";
      const dashArray = route.type === "uav" ? "10,10" : null;

      const polyline = L.polyline([route.from, route.to], {
        color,
        weight: 3,
        opacity: 0.7,
        dashArray,
      })
        .addTo(map)
        .bindPopup(
          `<b>${route.type === "truck" ? "Truck Route" : "UAV Path"}</b><br>Status: ${route.status}`
        );

      routesRef.current.push(polyline);
    });
  }, [routes]);

  return (
    <div className="flex-grow bg-gray-800 rounded-lg overflow-hidden relative" style={{ height: "600px" }}>
      <div ref={mapRef} style={{ width: "100%", height: "100%" }} />

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-gray-900 bg-opacity-90 p-4 rounded-lg text-sm z-[1000]">
        <h3 className="font-bold mb-2">Legend</h3>

        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            High Demand
          </div>

          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
            Medium Demand
          </div>

          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            Low Demand
          </div>

          <div className="flex items-center gap-2">
            🚛 Truck Route
          </div>

          <div className="flex items-center gap-2">
            🚁 UAV Path
          </div>

          <div className="flex items-center gap-2">
            🏭 Central Depot
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
