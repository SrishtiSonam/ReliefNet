import React, { useEffect, useState } from 'react';
import { getRequests, updateRequestStatus } from '../api/requestsApi';
import { Info, MapPin, Phone, User, Clock, AlertTriangle, CheckCircle, Clock3, Users } from 'lucide-react';
import { clsx } from 'clsx';

const RequestsView: React.FC = () => {
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const data = await getRequests();
      setRequests(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      await updateRequestStatus(id, newStatus);
      fetchRequests();
    } catch (e) {
      console.error(e);
      alert('Failed to update status');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
        <div>
          <h2 className="font-bold text-2xl flex items-center gap-3">
            <Info className="text-orange-500" /> Citizen Aid Requests
          </h2>
          <p className="text-sm text-gray-500 mt-1">Live feed of assistance requests submitted via the Public Portal.</p>
        </div>
        <div className="flex gap-4">
          <div className="bg-red-50 dark:bg-red-900/20 text-red-600 px-4 py-2 rounded-xl border border-red-100 dark:border-red-900/30 flex items-center gap-2 font-bold">
            <AlertTriangle size={16} /> {requests.filter(r => r.urgency === 'CRITICAL' && r.status === 'PENDING').length} Critical Pending
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-gray-400">Loading dispatcher feed...</div>
        ) : requests.length === 0 ? (
          <div className="col-span-full py-12 text-center text-gray-400">No active requests.</div>
        ) : requests.map((req) => (
          <div key={req.request_id} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm flex flex-col">
            <div className="flex justify-between items-start mb-4">
              <span className={clsx("px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wider", 
                req.urgency === 'CRITICAL' ? 'bg-red-100 text-red-700 border border-red-200' :
                req.urgency === 'HIGH' ? 'bg-orange-100 text-orange-700 border border-orange-200' :
                'bg-yellow-100 text-yellow-700 border border-yellow-200'
              )}>
                {req.urgency} URGENCY
              </span>
              <span className={clsx("px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-1",
                req.status === 'PENDING' ? 'bg-gray-100 text-gray-700' :
                req.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-700' :
                'bg-green-100 text-green-700'
              )}>
                {req.status === 'PENDING' && <Clock3 size={12} />}
                {req.status === 'IN_PROGRESS' && <AlertTriangle size={12} />}
                {req.status === 'RESOLVED' && <CheckCircle size={12} />}
                {req.status}
              </span>
            </div>

            <h3 className="font-bold text-lg mb-1">{req.need_type}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 flex-grow bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg">{req.description}</p>

            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300 mb-6">
              <p className="flex items-center gap-2"><MapPin size={16} className="text-gray-400 shrink-0"/> {req.address}</p>
              <p className="flex items-center gap-2"><User size={16} className="text-gray-400 shrink-0"/> {req.name}</p>
              <p className="flex items-center gap-2"><Phone size={16} className="text-gray-400 shrink-0"/> {req.contact}</p>
              <p className="flex items-center gap-2"><Users size={16} className="text-gray-400 shrink-0"/> {req.people_affected} People Affected</p>
            </div>

            <div className="grid grid-cols-3 gap-2 mt-auto border-t border-gray-100 dark:border-gray-800 pt-4">
              <button 
                onClick={() => handleStatusChange(req.request_id, 'PENDING')}
                disabled={req.status === 'PENDING'}
                className="py-2 text-xs font-bold rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 disabled:opacity-50"
              >
                PENDING
              </button>
              <button 
                onClick={() => handleStatusChange(req.request_id, 'IN_PROGRESS')}
                disabled={req.status === 'IN_PROGRESS'}
                className="py-2 text-xs font-bold rounded-lg bg-blue-100 hover:bg-blue-200 text-blue-700 disabled:opacity-50"
              >
                DISPATCH
              </button>
              <button 
                onClick={() => handleStatusChange(req.request_id, 'RESOLVED')}
                disabled={req.status === 'RESOLVED'}
                className="py-2 text-xs font-bold rounded-lg bg-green-100 hover:bg-green-200 text-green-700 disabled:opacity-50"
              >
                RESOLVE
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RequestsView;
