// pages/AuditLogPage.js
import React, { useState, useEffect } from 'react';

const AuditLogPage = ({ user, sessionId, apiBase }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const authHeaders = {
    'Authorization': `Bearer ${sessionId}`
  };

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    try {
      const response = await fetch(`${apiBase}/audit-logs`, {
        headers: authHeaders
      });

      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs);
      } else {
        setError('Failed to load audit logs');
      }
    } catch (err) {
      setError(`Error loading logs: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatDetails = (details) => {
    if (typeof details === 'object') {
      return JSON.stringify(details, null, 2);
    }
    return String(details);
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="text-center">Loading audit logs...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Audit Log</h1>
        <p className="text-gray-600">Track all system activities and decisions</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Details
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {logs.map((log, index) => (
                <tr key={log.id || index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {formatTimestamp(log.timestamp)}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {log.user}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      log.action.includes('error') ? 'bg-red-100 text-red-800' :
                      log.action.includes('accept') ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    <details className="cursor-pointer">
                      <summary className="hover:text-blue-600">
                        View details
                      </summary>
                      <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto">
                        {formatDetails(log.details)}
                      </pre>
                    </details>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {logs.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No audit logs found.
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogPage;