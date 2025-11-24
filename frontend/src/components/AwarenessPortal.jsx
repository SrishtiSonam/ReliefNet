import React, { useState } from 'react';

const AwarenessPortal = () => {
    const [query, setQuery] = useState("");
    const [answer, setAnswer] = useState(null);

    const askAI = async () => {
        if (!query) return;
        try {
            const res = await fetch('http://localhost:8000/api/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await res.json();
            setAnswer(data.explanation[0]);
        } catch (e) {
            setAnswer("Could not reach AI service.");
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold mb-6">Community Awareness & Safety</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-gray-800 p-6 rounded-lg">
                    <h3 className="text-xl font-bold mb-2 text-yellow-400">⚠️ Earthquake Safety</h3>
                    <ul className="list-disc pl-5 space-y-2 text-gray-300">
                        <li>Drop, Cover, and Hold On.</li>
                        <li>Stay away from windows and glass.</li>
                        <li>If outdoors, stay in open areas away from buildings.</li>
                    </ul>
                </div>
                <div className="bg-gray-800 p-6 rounded-lg">
                    <h3 className="text-xl font-bold mb-2 text-blue-400">Flood Preparedness</h3>
                    <ul className="list-disc pl-5 space-y-2 text-gray-300">
                        <li>Move to higher ground immediately.</li>
                        <li>Do not walk or drive through moving water.</li>
                        <li>Keep an emergency kit ready.</li>
                    </ul>
                </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-4">Ask the AI Safety Assistant</h3>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Ask about allocation logic or safety tips..."
                        className="flex-grow p-3 rounded bg-gray-700 text-white border border-gray-600 focus:border-blue-500 outline-none"
                    />
                    <button onClick={askAI} className="bg-blue-600 px-6 py-3 rounded font-bold hover:bg-blue-700">Ask</button>
                </div>
                {answer && (
                    <div className="mt-4 p-4 bg-gray-700 rounded border-l-4 border-blue-400">
                        <p className="font-bold text-blue-300 mb-1">AI Response:</p>
                        <p>{answer}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AwarenessPortal;
