import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LayoutDashboard, FileText, Briefcase, TrendingUp, Map, MessageSquare, MessageCircle } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import ResumeUpload from './pages/ResumeUpload';
import Opportunities from './pages/Opportunities';
import LearningRoadmap from './pages/LearningRoadmap';
import AgentChat from './pages/AgentChat';
import Compare from './pages/Compare';

function Sidebar() {
  const location = useLocation();
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/compare', label: 'Compare', icon: <Briefcase size={20} /> },
    { path: '/roadmap', label: 'Roadmap', icon: <Map size={20} /> },
    { path: '/chat', label: 'AI Chat', icon: <MessageSquare size={20} /> },
  ];

  return (
    <div className="w-64 bg-surface border-r border-gray-800 flex flex-col h-screen">
      <div className="p-6">
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
          Path Pilot
        </h1>
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
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-background text-textPrimary font-sans">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/roadmap" element={<LearningRoadmap />} />
            <Route path="/chat" element={<AgentChat />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
