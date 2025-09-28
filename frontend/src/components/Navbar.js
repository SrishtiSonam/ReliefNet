// frontend/src/components/Navbar.js
import React from 'react';

const Navbar = ({ user, onLogout }) => {
  return (
    <nav className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold">SDPDIAP</h1>
            </div>
            
            <div className="hidden md:flex space-x-1">
              <a href="/" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-white hover:bg-opacity-20 transition-colors">
                Dashboard
              </a>
              <a href="/simulation" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-white hover:bg-opacity-20 transition-colors">
                Simulation
              </a>
              <a href="/audit" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-white hover:bg-opacity-20 transition-colors">
                Audit Log
              </a>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="text-sm font-medium">{user.username}</span>
            </div>
            
            <button
              onClick={onLogout}
              className="px-3 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-md text-sm font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
