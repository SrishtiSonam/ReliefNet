import React, { useState } from 'react';
import axios from 'axios';

export default function DataIngestion() {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('');

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            setStatus('Uploading...');
            await axios.post('http://localhost:8000/api/data/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setStatus('Upload successful!');
        } catch (error) {
            console.error(error);
            setStatus('Failed to upload data.');
        }
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Data Ingestion</h1>
            <div className="bg-white p-6 rounded-lg shadow-sm border max-w-lg">
                <p className="mb-4 text-gray-600">Upload historical CSV datasets, topography data, or warehouse configurations to feed the Machine Learning pipeline.</p>
                <form onSubmit={handleUpload}>
                    <input
                        type="file"
                        className="mb-4 block w-full text-sm text-slate-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
                        onChange={(e) => setFile(e.target.files[0])}
                    />
                    <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700">
                        Upload to Pipeline
                    </button>
                </form>
                {status && <p className="mt-4 text-sm font-semibold">{status}</p>}
            </div>
        </div>
    );
}
