import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function FloodEvents() {
    const [events, setEvents] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:5000/api/flood-events')
            .then(res => setEvents(res.data))
            .catch(err => console.error("Error fetching flood events", err));
    }, []);

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Flood Events Archive</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {events.map(event => (
                    <div key={event._id} className="p-4 border rounded-lg shadow-sm bg-white">
                        <h3 className="font-bold text-lg">{event.event_name}</h3>
                        <p className="text-sm text-gray-600">District: {event.district_name}</p>
                        <p className="text-sm">Severity: <span className="font-semibold">{event.severity}</span></p>
                        <p className="text-sm">Affected: {event.affected_population?.toLocaleString() || 0}</p>
                    </div>
                ))}
                {events.length === 0 && (
                    <div className="col-span-full text-center text-gray-500">
                        No active or historical flood events.
                    </div>
                )}
            </div>
        </div>
    );
}
