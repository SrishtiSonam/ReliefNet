import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Districts() {
    const [districts, setDistricts] = useState([]);

    useEffect(() => {
        // Assuming Express acts as a passthrough or API
        axios.get('http://localhost:5000/api/districts')
            .then(res => setDistricts(res.data))
            .catch(err => console.error("Error fetching districts", err));
    }, []);

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Districts Management</h1>
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200 shadow-sm rounded-lg">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="py-2 px-4 border-b">District Name</th>
                            <th className="py-2 px-4 border-b">State</th>
                            <th className="py-2 px-4 border-b">Population</th>
                            <th className="py-2 px-4 border-b">Vulnerability Index</th>
                        </tr>
                    </thead>
                    <tbody>
                        {districts.map(d => (
                            <tr key={d._id} className="text-center border-b">
                                <td className="py-2 px-4">{d.name}</td>
                                <td className="py-2 px-4">{d.state_name || 'N/A'}</td>
                                <td className="py-2 px-4">{d.population?.toLocaleString() || 'N/A'}</td>
                                <td className="py-2 px-4">{d.vulnerability_score || 'N/A'}</td>
                            </tr>
                        ))}
                        {districts.length === 0 && (
                            <tr>
                                <td colSpan="4" className="py-4 text-center text-gray-500">No districts found.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
