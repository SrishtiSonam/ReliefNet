import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// Custom icons for different types
const disasterIcon = L.divIcon({
  html: `<div style="background-color: red; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(255,0,0,0.8); animation: pulse 2s infinite;"></div>`,
  className: '',
  iconSize: [20, 20],
  iconAnchor: [10, 10]
});

const warehouseIcon = L.divIcon({
  html: `<div style="background-color: #0ea5e9; width: 16px; height: 16px; border-radius: 4px; border: 2px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.5);"></div>`,
  className: '',
  iconSize: [16, 16],
  iconAnchor: [8, 8]
});

interface ReliefMapProps {
  center?: [number, number];
  zoom?: number;
  markers?: Array<{
    position: [number, number];
    label: string;
    type: 'warehouse' | 'district' | 'disaster' | 'impacted';
    details?: string;
  }>;
  circles?: Array<{
    center: [number, number];
    radius: number; // in meters
    color: string;
    fillColor: string;
    fillOpacity: number;
  }>;
}

const ChangeView = ({ center, zoom }: { center: [number, number], zoom: number }) => {
  const map = import('react-leaflet').then(m => m.useMap?.());
  // Basic hack for flyTo, could be better implemented but keeping it simple for now
  return null;
};

const ReliefMap: React.FC<ReliefMapProps> = ({ 
  center = [20.5937, 78.9629], // Center of India
  zoom = 5,
  markers = [],
  circles = []
}) => {
  return (
    <div className="w-full h-full min-h-[400px] bg-gray-100 dark:bg-gray-800 rounded-2xl overflow-hidden shadow-inner border border-gray-200 dark:border-gray-700 relative z-0">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        
        {circles.map((circle, idx) => (
          <Circle 
            key={`circle-${idx}`}
            center={circle.center}
            radius={circle.radius}
            pathOptions={{
              color: circle.color,
              fillColor: circle.fillColor,
              fillOpacity: circle.fillOpacity,
              weight: 2
            }}
          />
        ))}

        {markers.map((marker, idx) => {
          let mIcon = DefaultIcon;
          if (marker.type === 'disaster') mIcon = disasterIcon;
          if (marker.type === 'warehouse') mIcon = warehouseIcon;
          if (marker.type === 'impacted') {
            mIcon = L.divIcon({
              html: `<div style="background-color: #f97316; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
              className: '',
              iconSize: [12, 12],
              iconAnchor: [6, 6]
            });
          }

          return (
            <Marker key={idx} position={marker.position} icon={mIcon}>
              <Popup>
                <div className="p-1">
                  <p className="font-bold text-sm">{marker.label}</p>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider">{marker.type}</p>
                  {marker.details && <p className="text-xs mt-1 text-gray-700">{marker.details}</p>}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default ReliefMap;
