import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LayoutDashboard, FileText, Briefcase, TrendingUp, Map, HelpCircle, MessageCircle, Compass, Shield } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import ResumeUpload from './pages/ResumeUpload';
import Opportunities from './pages/Opportunities';
import LearningRoadmap from './pages/LearningRoadmap';
import AgentChat from './pages/AgentChat';
import Compare from './pages/Compare';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute, AdminRoute } from './components/ProtectedRoute';

function Sidebar() {
  const location = useLocation();
  const { user, isAdmin, logout } = useAuth();
  
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/compare', label: 'Compare', icon: <Briefcase size={20} /> },
    { path: '/roadmap', label: 'Roadmap', icon: <Map size={20} /> },
    { path: '/chat', label: 'FAQ', icon: <HelpCircle size={20} /> },
  ];

  if (isAdmin) {
    menuItems.push({ path: '/admin', label: 'Admin Panel', icon: <Shield size={20} /> });
  }

  return (
    <div className="w-64 bg-surface border-r border-gray-800 flex flex-col h-screen">
      <div className="p-6 border-b border-gray-800/80">
        <div className="flex items-center space-x-3">
          <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 p-[1px] shadow-lg shadow-blue-500/20 group">
            <div className="w-full h-full bg-gray-950/90 rounded-[11px] flex items-center justify-center backdrop-blur-md transition-all group-hover:bg-gray-900/60">
              <Compass className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-surface animate-ping" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-surface" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-xl font-extrabold tracking-tight text-white">
                Path<span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">Pilot</span>
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold tracking-wider uppercase bg-blue-500/10 text-cyan-400 border border-cyan-500/30 rounded-md">
                AI
              </span>
            </div>
            <p className="text-[11px] font-medium text-gray-400 tracking-wider uppercase mt-0.5">
              Career Agent
            </p>
          </div>
        </div>
      </div>
      <nav className="flex-1 mt-6">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center space-x-3 px-6 py-3 transition-colors ${
              location.pathname === item.path
                ? 'bg-primary/10 text-primary border-r-4 border-primary'
                : 'text-textSecondary hover:text-textPrimary hover:bg-gray-800'
            }`}
          >
            {item.icon}
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center justify-between px-2 mb-4">
          <div className="flex flex-col">
            <span className="text-sm font-medium text-white">{user?.username}</span>
            <span className="text-xs text-gray-500">{user?.role?.toUpperCase()}</span>
          </div>
        </div>
        <button 
          onClick={logout}
          className="w-full py-2 px-4 bg-gray-900 hover:bg-red-500/10 text-gray-400 hover:text-red-400 rounded-lg text-sm font-medium transition-colors border border-gray-800 hover:border-red-500/30"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}

function AppRoutes() {
  const { user } = useAuth();
  const location = useLocation();
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <div className="flex min-h-screen bg-background text-textPrimary font-sans">
      {!isAuthPage && <Sidebar />}
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/compare" element={<ProtectedRoute><Compare /></ProtectedRoute>} />
          <Route path="/roadmap" element={<ProtectedRoute><LearningRoadmap /></ProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><AgentChat /></ProtectedRoute>} />
          
          {/* Admin Routes */}
          <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
