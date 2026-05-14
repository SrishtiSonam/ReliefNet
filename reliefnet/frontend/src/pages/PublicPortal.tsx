import React, { useState } from 'react';
import { ShieldAlert, MapPin, Phone, Info, Navigation, ArrowRight, X, Heart, BookOpen, AlertTriangle, Send } from 'lucide-react';
import { Link } from 'react-router-dom';

const PublicPortal: React.FC = () => {
  const [activeModal, setActiveModal] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 relative">
      {/* Navbar */}
      <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md sticky top-0 z-40 border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-relief-600 rounded-lg flex items-center justify-center text-white font-bold">RN</div>
              <span className="font-bold text-xl tracking-tight text-gray-900 dark:text-white">ReliefNet</span>
            </div>
            <div className="flex gap-4">
              <button onClick={() => setActiveModal('guidelines')} className="text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-2 hidden sm:block">
                Emergency Guidelines
              </button>
              <button onClick={() => setActiveModal('volunteer')} className="text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors px-3 py-2 hidden sm:block">
                Volunteering
              </button>
              <Link to="/login" className="text-sm font-bold bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-4 py-2 rounded-lg hover:opacity-90 transition-opacity">
                Responder Login
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative pt-16 pb-32 flex content-center items-center justify-center min-h-[60vh]">
        <div className="absolute top-0 w-full h-full bg-center bg-cover bg-[url('https://images.unsplash.com/photo-1547683905-f686c993aae5?q=80&w=2070&auto=format&fit=crop')]">
          <span className="w-full h-full absolute opacity-75 bg-gradient-to-b from-gray-900/90 to-gray-900/95" />
        </div>
        <div className="container relative mx-auto px-4 text-center z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 text-sm font-bold mb-6 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-red-500" /> Active Alert: Monsoon Flooding
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-6">
            Disaster Information & <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-relief-400 to-blue-400">Response Portal</span>
          </h1>
          <p className="mt-4 text-lg text-gray-300 max-w-2xl mx-auto mb-10">
            Real-time updates on active disaster zones, nearest relief shelters, and critical emergency resources. Stay informed and safe.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button onClick={() => setActiveModal('shelters')} className="px-8 py-4 bg-relief-600 hover:bg-relief-500 text-white font-bold rounded-xl shadow-lg shadow-relief-600/30 transition-all flex items-center justify-center gap-2">
              <MapPin size={20} /> Find Nearest Shelter
            </button>
            <button onClick={() => setActiveModal('contacts')} className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl backdrop-blur-md border border-white/10 transition-all flex items-center justify-center gap-2">
              <Phone size={20} /> Emergency Contacts
            </button>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 -mt-20 relative z-20 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          <div onClick={() => setActiveModal('shelters')} className="cursor-pointer bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-100 dark:border-gray-700 hover:-translate-y-1 transition-transform duration-300 group">
            <div className="w-12 h-12 bg-relief-50 dark:bg-relief-900/20 text-relief-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Navigation size={24} />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Relief Shelters</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-4">Locate active relief camps, their current capacity, and available facilities.</p>
            <button className="text-relief-600 font-semibold text-sm flex items-center gap-1 group-hover:gap-2 transition-all">
              Find Shelters <ArrowRight size={16} />
            </button>
          </div>

          <div onClick={() => setActiveModal('request')} className="cursor-pointer bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-100 dark:border-gray-700 hover:-translate-y-1 transition-transform duration-300 group">
            <div className="w-12 h-12 bg-orange-50 dark:bg-orange-900/20 text-orange-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Info size={24} />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Resource Requests</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-4">Request specific aid or report critical shortages in your community.</p>
            <button className="text-orange-500 font-semibold text-sm flex items-center gap-1 group-hover:gap-2 transition-all">
              Submit Request <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Dynamic Modals */}
      {activeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white dark:bg-gray-900 rounded-3xl w-full max-w-lg shadow-2xl border border-gray-200 dark:border-gray-800 overflow-hidden flex flex-col">
            <div className="flex justify-between items-center p-6 border-b border-gray-100 dark:border-gray-800">
              <h2 className="font-bold text-xl flex items-center gap-2">
                {activeModal === 'guidelines' && <><BookOpen className="text-relief-600" /> Emergency Guidelines</>}
                {activeModal === 'volunteer' && <><Heart className="text-red-500" /> Volunteer Registration</>}
                {activeModal === 'map' && <><ShieldAlert className="text-orange-500" /> Active Alert Zones</>}
                {activeModal === 'shelters' && <><Navigation className="text-relief-600" /> Nearest Shelters</>}
                {activeModal === 'request' && <><Info className="text-blue-500" /> Request Assistance</>}
                {activeModal === 'contacts' && <><Phone className="text-green-500" /> Emergency Contacts</>}
              </h2>
              <button onClick={() => setActiveModal(null)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              {/* Guidelines Content */}
              {activeModal === 'guidelines' && (
                <div className="space-y-4">
                  <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-xl border border-orange-100 dark:border-orange-800 text-sm">
                    <h4 className="font-bold text-orange-800 dark:text-orange-400 mb-2">Flood Safety protocol</h4>
                    <ul className="list-disc pl-5 space-y-1 text-orange-700 dark:text-orange-300">
                      <li>Move to higher ground immediately.</li>
                      <li>Do not walk or drive through flood waters. 6 inches of water can knock you down.</li>
                      <li>Disconnect electrical appliances if safe to do so.</li>
                    </ul>
                  </div>
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800 text-sm">
                    <h4 className="font-bold text-blue-800 dark:text-blue-400 mb-2">Evacuation Checklist</h4>
                    <ul className="list-disc pl-5 space-y-1 text-blue-700 dark:text-blue-300">
                      <li>Important documents (ID, Insurance)</li>
                      <li>3-day supply of water and non-perishable food</li>
                      <li>First aid kit and prescription medications</li>
                    </ul>
                  </div>
                </div>
              )}

              {/* Volunteer Content */}
              {activeModal === 'volunteer' && (
                <form className="space-y-4" onSubmit={e => { e.preventDefault(); setActiveModal(null); alert('Application submitted successfully!'); }}>
                  <p className="text-sm text-gray-500 mb-4">Join our network of disaster response volunteers. We are currently mobilizing teams for the Maharashtra floods.</p>
                  <input required type="text" placeholder="Full Name" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" />
                  <input required type="email" placeholder="Email Address" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" />
                  <select className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none text-gray-500">
                    <option>Medical Assistance</option>
                    <option>Logistics & Transport</option>
                    <option>Search & Rescue</option>
                    <option>General Support</option>
                  </select>
                  <button type="submit" className="w-full py-3 bg-relief-600 text-white font-bold rounded-xl mt-4">Submit Application</button>
                </form>
              )}

              {/* Shelters Content */}
              {activeModal === 'shelters' && (
                <div className="space-y-4">
                  {[
                    { 
                      n: 'Mumbai Central High School', dist: '1.2 km', cap: '450/500',
                      addr: 'Dr Anandrao Nair Marg, Mumbai Central, 400008',
                      coords: '18.9750° N, 72.8258° E',
                      items: ['Hot Meals', 'First Aid', 'Blankets']
                    },
                    { 
                      n: 'Community Sports Complex', dist: '3.5 km', cap: '120/800',
                      addr: 'Andheri West Sports Club, Veera Desai Rd, 400053',
                      coords: '19.1278° N, 72.8336° E',
                      items: ['Drinking Water', 'Medical Camp', 'Baby Supplies']
                    },
                    { 
                      n: 'City Hospital Safe Zone', dist: '5.0 km', cap: 'Full',
                      addr: 'Parel, Opposite KEM Hospital, 400012',
                      coords: '19.0033° N, 72.8400° E',
                      items: ['Emergency ICU', 'Trauma Care', 'Oxygen Cylinders']
                    }
                  ].map((s, i) => (
                    <div key={i} className="flex flex-col p-4 border border-gray-100 dark:border-gray-800 rounded-xl bg-white dark:bg-gray-800 shadow-sm">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-bold text-base text-gray-900 dark:text-white">{s.n}</p>
                          <p className="text-xs font-medium text-relief-600 mb-1 flex items-center gap-1"><Navigation size={12} /> {s.dist} away</p>
                        </div>
                        <span className={`text-xs font-bold px-2 py-1 rounded ${s.cap === 'Full' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                          {s.cap} Capacity
                        </span>
                      </div>
                      
                      <div className="space-y-1.5 mt-2 text-sm text-gray-600 dark:text-gray-400">
                        <p className="flex items-start gap-2">
                          <MapPin size={14} className="mt-0.5 shrink-0" /> 
                          <span>{s.addr}<br/><span className="text-[10px] uppercase font-mono opacity-60">GPS: {s.coords}</span></span>
                        </p>
                      </div>

                      <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-700">
                        <p className="text-[10px] font-bold uppercase text-gray-400 mb-2">Resources Available:</p>
                        <div className="flex flex-wrap gap-2">
                          {s.items.map(item => (
                            <span key={item} className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-md text-gray-700 dark:text-gray-300">
                              {item}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Request Content */}
              {activeModal === 'request' && (
                <form className="space-y-4" onSubmit={async e => { 
                  e.preventDefault(); 
                  const fd = new FormData(e.target as HTMLFormElement);
                  const data = Object.fromEntries(fd.entries());
                  try {
                    const { submitRequest } = await import('../api/requestsApi');
                    await submitRequest({
                      name: data.name,
                      contact: data.contact,
                      need_type: data.need_type,
                      address: data.address,
                      people_affected: parseInt(data.people as string) || 1,
                      urgency: data.urgency,
                      description: data.desc
                    });
                    setActiveModal(null); 
                    alert('Request logged directly to Central Dispatch. Help is on the way.');
                  } catch (err) {
                    console.error(err);
                    alert('Failed to submit request.');
                  }
                }}>
                  <div className="grid grid-cols-2 gap-4">
                    <input name="name" required type="text" placeholder="Full Name" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" />
                    <input name="contact" required type="text" placeholder="Phone Number" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" />
                  </div>
                  <input name="address" required type="text" placeholder="Precise Location / Address" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" />
                  
                  <div className="grid grid-cols-2 gap-4">
                    <select name="need_type" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none text-gray-500">
                      <option value="Medical Emergency">Medical Emergency</option>
                      <option value="Food & Water">Food & Water Shortage</option>
                      <option value="Evacuation">Evacuation Support Required</option>
                      <option value="Shelter">Temporary Shelter Needed</option>
                    </select>
                    <select name="urgency" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none text-gray-500">
                      <option value="CRITICAL">CRITICAL (Immediate)</option>
                      <option value="HIGH">HIGH (Within 6 Hours)</option>
                      <option value="MEDIUM">MEDIUM (Within 24 Hours)</option>
                    </select>
                  </div>

                  <input name="people" required type="number" min="1" placeholder="Number of people affected" className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none" />

                  <textarea name="desc" required rows={3} placeholder="Describe the specific situation, injuries, or hazards..." className="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 outline-none resize-none"></textarea>
                  
                  <button type="submit" className="w-full py-3 bg-orange-500 hover:bg-orange-600 text-white font-bold rounded-xl mt-4 flex justify-center items-center gap-2">
                    <Send size={18} /> Transmit Request
                  </button>
                </form>
              )}

              {/* Map/Disasters Content */}
              {activeModal === 'map' && (
                <div className="text-center py-8">
                  <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                    <MapPin className="text-gray-400" size={32} />
                  </div>
                  <h3 className="font-bold text-lg mb-2">Live Map Loading...</h3>
                  <p className="text-gray-500 text-sm">Connecting to GIS database to retrieve active disaster boundaries for Maharashtra.</p>
                </div>
              )}

              {/* Contacts Content */}
              {activeModal === 'contacts' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                    <span className="font-bold">National Emergency Number</span>
                    <a href="tel:112" className="text-relief-600 font-bold bg-relief-50 dark:bg-relief-900/20 px-3 py-1 rounded-lg">112</a>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                    <span className="font-bold">Ambulance</span>
                    <a href="tel:102" className="text-relief-600 font-bold bg-relief-50 dark:bg-relief-900/20 px-3 py-1 rounded-lg">102</a>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                    <span className="font-bold">Disaster Management Services</span>
                    <a href="tel:108" className="text-relief-600 font-bold bg-relief-50 dark:bg-relief-900/20 px-3 py-1 rounded-lg">108</a>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PublicPortal;
