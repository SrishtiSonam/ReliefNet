import React, { useState } from 'react';
import { ArrowRight, ShieldCheck, Mail, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Navigate to dashboard on success
    navigate('/');
  };

  return (
    <div className="min-h-screen flex w-full bg-gray-950 text-white selection:bg-relief-500 selection:text-white">
      {/* Left side: Hero Image / Branding */}
      <div className="hidden lg:flex w-1/2 relative bg-gray-900 overflow-hidden items-center justify-center">
        {/* Background Image overlay */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-60"
          style={{ backgroundImage: `url('/login_hero.png')` }}
        />
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/60 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-gray-950/80 via-transparent to-transparent" />
        
        <div className="relative z-10 p-16 flex flex-col h-full justify-between w-full max-w-2xl">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-relief-500 to-relief-700 rounded-xl flex items-center justify-center shadow-lg shadow-relief-500/30">
              <ShieldCheck size={28} className="text-white" />
            </div>
            <span className="text-2xl font-bold tracking-tight">ReliefNet</span>
          </div>

          <div className="space-y-6">
            <h1 className="text-5xl font-extrabold leading-tight">
              Intelligent <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-relief-400 to-blue-500">
                Disaster Response.
              </span>
            </h1>
            <p className="text-lg text-gray-400 max-w-md">
              AI-driven logistics, simulation, and resource allocation platform for emergency coordinators and responders.
            </p>
          </div>

          <div className="flex items-center gap-4 text-sm font-medium text-gray-500">
            <p>&copy; 2026 ReliefNet Systems</p>
            <div className="w-1 h-1 bg-gray-700 rounded-full" />
            <p>Secure Portal</p>
          </div>
        </div>
      </div>

      {/* Right side: Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12">
        <div className="w-full max-w-md space-y-10">
          <div className="text-center lg:text-left space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">Welcome back</h2>
            <p className="text-gray-400">Sign in to the coordinator dashboard.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 ml-1">Email Address</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                    <Mail size={18} />
                  </div>
                  <input 
                    type="email" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full pl-11 pr-4 py-3.5 bg-gray-900/50 border border-gray-800 rounded-xl focus:ring-2 focus:ring-relief-500 focus:border-relief-500 outline-none transition-all placeholder-gray-600 backdrop-blur-sm"
                    placeholder="coordinator@reliefnet.gov"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label className="text-sm font-medium text-gray-300">Password</label>
                  <a href="#" className="text-xs font-medium text-relief-500 hover:text-relief-400">Forgot password?</a>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                    <Lock size={18} />
                  </div>
                  <input 
                    type="password" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full pl-11 pr-4 py-3.5 bg-gray-900/50 border border-gray-800 rounded-xl focus:ring-2 focus:ring-relief-500 focus:border-relief-500 outline-none transition-all placeholder-gray-600 backdrop-blur-sm"
                    placeholder="••••••••"
                  />
                </div>
              </div>
            </div>

            <button 
              type="submit" 
              className="group w-full py-3.5 bg-gradient-to-r from-relief-600 to-relief-500 hover:from-relief-500 hover:to-relief-400 text-white rounded-xl font-semibold shadow-[0_0_20px_rgba(14,165,233,0.3)] hover:shadow-[0_0_25px_rgba(14,165,233,0.5)] transition-all flex items-center justify-center gap-2"
            >
              Sign In to Command Center
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </form>

          <div className="pt-8 border-t border-gray-800 text-center text-sm text-gray-500">
            <p>Need access? <a href="#" className="text-relief-500 hover:text-relief-400 font-medium">Contact Administrator</a></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
