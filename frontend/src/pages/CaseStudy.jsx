import React from 'react';

export default function CaseStudy() {
    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Case Studies</h1>
            <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h2 className="text-xl font-bold mb-2">Kerala Floods (2018)</h2>
                <p className="text-gray-700 mb-4">
                    The 2018 Kerala floods were a catastrophic event... (Analysis and Retrospective).
                    Below are the simulated distributions vs actual response metrics.
                </p>
                {/* Placeholder for complex case study UI */}
                <div className="h-64 bg-gray-100 rounded flex items-center justify-center border-dashed border-2 border-gray-300">
                    <span className="text-gray-500">Case Study Visualization</span>
                </div>
            </div>
        </div>
    );
}
