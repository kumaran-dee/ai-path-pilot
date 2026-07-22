import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getLinks, updateLinks, scanProfile, uploadResume, getDashboardSummary } from '../services/api';
import { FileText, Globe, Briefcase, Terminal, Cpu, Loader2, Sparkles, GraduationCap, Code, BookOpen, ChevronRight, CheckCircle, XCircle, MessageCircle, ExternalLink } from 'lucide-react';

export default function Dashboard() {
  const [links, setLinks] = useState({
    resume: null,
    portfolio: null,
    linkedin: null,
    github: null,
    leetcode: null
  });

  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState(null);
  const [editingSlot, setEditingSlot] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [editError, setEditError] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const validateLink = (id, url) => {
    if (!url || url.trim() === '') return '';
    try {
      const parsed = new URL(url);
      if (parsed.protocol !== 'https:') return 'Must be a valid https:// URL';
      
      if (id === 'linkedin' && !parsed.hostname.includes('linkedin.com')) {
        return 'Must be a valid linkedin.com URL';
      }
      if (id === 'github' && !parsed.hostname.includes('github.com')) {
        return 'Must be a valid github.com URL';
      }
      if (id === 'leetcode' && !parsed.hostname.includes('leetcode.com')) {
        return 'Must be a valid leetcode.com URL';
      }
      return '';
    } catch (e) {
      return 'Please enter a valid URL (e.g., https://...)';
    }
  };

  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    getLinks()
      .then(res => {
        setLinks(res.data);
      })
      .catch(err => {
        console.error("Failed to fetch links", err);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const handleSave = async (key, val) => {
    const error = validateLink(key, val);
    if (error) {
      setEditError(error);
      return;
    }
    const newLinks = { ...links, [key]: val };
    setLinks(newLinks);
    setEditingSlot(null);
    setEditError('');
    try {
      await updateLinks({ [key]: val });
    } catch (err) {
      console.error("Failed to save to backend", err);
    }
  };

  const hasData = Object.values(links).some(val => val !== null && val.trim && val.trim() !== '');

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await uploadResume(formData);
      setLinks({ ...links, resume: file.name });
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to upload resume.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleScan = async () => {
    setIsScanning(true);
    setScanResults(null);
    try {
      const res = await scanProfile();
      setScanResults(res.data);
      // In a real app, this would show the scan results UI, which we removed earlier.
    } catch (err) {
      console.error("Scan failed", err);
      alert("Failed to connect to the AI backend.");
    } finally {
      setIsScanning(false);
    }
  };

  const getSearchUrl = (item, category) => {
    const cleanItem = item.replace(/\s*\(LinkedIn\)|\s*\(Unstop\)|\s*\(LeetCode\)/ig, '').trim();
    const query = encodeURIComponent(cleanItem);

    switch(category) {
      case 'jobs':
      case 'internships':
        return `https://www.linkedin.com/jobs/search/?keywords=${query}`;
      case 'hackathons':
      case 'workshops':
        return `https://www.google.com/search?q=site%3Aunstop.com+${query}`;
      case 'leetcode_problems':
        return `https://leetcode.com/problemset/all/?search=${query}`;
      default:
        return '#';
    }
  };

  const slots = [
    { id: 'resume', label: 'Upload Resume', subtext: 'PDF or DOCX', icon: <FileText size={28} className="mb-3 text-gray-300" /> },
    { id: 'portfolio', label: 'Portfolio', subtext: 'Visit Profile', icon: <Globe size={28} className="mb-3 text-blue-400" /> },
    { id: 'linkedin', label: 'LinkedIn', subtext: 'Visit Profile', icon: <Briefcase size={28} className="mb-3 text-amber-600" /> },
    { id: 'github', label: 'GitHub', subtext: 'Visit Profile', icon: <Terminal size={28} className="mb-3 text-pink-400" /> },
    { id: 'leetcode', label: 'LeetCode', subtext: 'Visit Profile', icon: <Cpu size={28} className="mb-3 text-yellow-500" /> }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-8 pb-24 text-white"
    >
      <div className="mb-10">
        <h1 className="text-3xl font-bold">Dashboard <span className="text-primary">Overview</span></h1>
        <p className="text-gray-400 mt-2 text-sm">Your career health at a glance</p>
      </div>
      
      {/* Row 1: Profile Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-8">
        {slots.map((slot) => {
          const url = links[slot.id] ? (links[slot.id].startsWith('http') ? links[slot.id] : `https://${links[slot.id]}`) : '#';
          const isEditing = editingSlot === slot.id;
          const hasLink = !!links[slot.id];
          
          if (slot.id === 'resume') {
            return (
              <div key={slot.id} className="bg-[#1e2128] p-6 rounded-2xl border border-gray-800 min-h-[140px] flex flex-col items-center justify-center transition-all hover:border-gray-600 relative">
                <label className="flex flex-col items-center w-full cursor-pointer hover:opacity-80 transition-opacity">
                  {isUploading ? <Loader2 size={28} className="mb-3 text-gray-300 animate-spin" /> : slot.icon}
                  <h3 className="font-semibold mb-1 text-center text-sm">{slot.label}</h3>
                  <span className="text-xs text-gray-500 text-center block w-full truncate px-2">
                    {links.resume ? links.resume : 'Click to Upload'}
                  </span>
                  <input type="file" className="hidden" accept=".pdf,.doc,.docx" onChange={handleFileUpload} disabled={isUploading} />
                </label>
              </div>
            );
          }

          return (
            <div key={slot.id} className="bg-[#1e2128] p-6 rounded-2xl border border-gray-800 min-h-[140px] flex flex-col items-center justify-center transition-all hover:border-gray-600 relative">
              {isEditing ? (
                <div className="flex flex-col items-center w-full">
                  <input 
                    type="text" 
                    value={editValue} 
                    onChange={(e) => {
                      const val = e.target.value;
                      setEditValue(val);
                      setEditError(validateLink(slot.id, val));
                    }}
                    placeholder="Enter URL (https://...)"
                    className={`w-full bg-gray-900 border ${editError ? 'border-red-500 focus:ring-red-500' : 'border-gray-700'} rounded p-2 text-sm text-white mb-1 outline-none`}
                    autoFocus
                  />
                  {editError && <span className="text-red-400 text-[10px] mb-2 w-full text-left">{editError}</span>}
                  <div className="flex space-x-2 w-full mt-1">
                    <button 
                      onClick={() => handleSave(slot.id, editValue)} 
                      disabled={!!editError}
                      className="flex-1 bg-primary text-white text-xs py-1 rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Save
                    </button>
                    <button onClick={() => {
                      setEditingSlot(null);
                      setEditError('');
                    }} className="flex-1 bg-gray-700 text-white text-xs py-1 rounded hover:bg-gray-600">Cancel</button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center w-full">
                  <a 
                    href={hasLink ? url : '#'}
                    target={hasLink ? "_blank" : "_self"}
                    rel="noopener noreferrer"
                    className="flex flex-col items-center w-full cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={(e) => {
                      if (!hasLink) {
                        e.preventDefault();
                        setEditingSlot(slot.id);
                        setEditValue('');
                        setEditError('');
                      }
                    }}
                  >
                    {slot.icon}
                    <h3 className="font-semibold mb-1 text-center text-sm">{slot.label}</h3>
                    <span className="text-xs text-gray-500 text-center block w-full">{hasLink ? 'Visit Profile' : '+ Add Link'}</span>
                  </a>
                  {hasLink && (
                    <button 
                      onClick={() => {
                        setEditingSlot(slot.id);
                        setEditValue(links[slot.id] || '');
                        setEditError('');
                      }}
                      className="absolute top-2 right-2 text-gray-500 hover:text-white text-xs"
                    >
                      Edit
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>


      {/* WhatsApp Community Banner */}
      <div className="mt-8 bg-[#00A884] rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between relative overflow-hidden shadow-lg border border-[#00c59a]">
        {/* Decorative background circles */}
        <div className="absolute -right-20 -top-20 w-64 h-64 border-[30px] border-white/5 rounded-full pointer-events-none"></div>
        <div className="absolute -right-10 -bottom-10 w-48 h-48 border-[20px] border-white/5 rounded-full pointer-events-none"></div>

        <div className="flex items-center space-x-6 z-10 w-full md:w-auto">
          <div className="hidden sm:flex bg-white/20 p-4 rounded-2xl items-center justify-center backdrop-blur-sm border border-white/30 shrink-0">
            <MessageCircle size={36} className="text-white" />
          </div>
          <div>
            <h2 className="text-xl md:text-2xl font-bold text-white mb-2">Join the Official WhatsApp Community</h2>
            <p className="text-white/90 text-sm md:text-base max-w-2xl leading-relaxed">
              Connect with ambitious professionals. Share career milestones, discuss AI-powered roadmaps, and get tips to land your dream role.
            </p>
          </div>
        </div>

        <a 
          href="https://chat.whatsapp.com/GDXtxLFZdvs228lJm6WBLd"
          target="_blank"
          rel="noopener noreferrer"
          className="mt-6 md:mt-0 flex items-center justify-center space-x-2 bg-white text-[#00A884] font-bold px-6 py-3 rounded-xl hover:bg-gray-50 transition-colors shrink-0 shadow-sm z-10 w-full md:w-auto"
        >
          <span>Join WhatsApp Group</span>
          <ExternalLink size={18} />
        </a>
      </div>

      {/* Action Button */}
      <div className="mt-12 flex justify-center">
        <button 
          disabled={!hasData || isScanning}
          onClick={handleScan}
          className="flex items-center justify-center space-x-2 px-10 py-4 bg-primary text-white font-bold text-lg rounded-xl shadow-[0_0_15px_rgba(59,130,246,0.4)] disabled:shadow-none disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed hover:bg-blue-600 transition-all min-w-[250px]"
        >
          {isScanning ? (
            <><Loader2 className="animate-spin" size={24} /><span>SCANNING AI...</span></>
          ) : (
            <><Sparkles size={24} /><span>SCAN PROFILE</span></>
          )}
        </button>
      </div>

      {/* Linked Profile Details */}
      {scanResults && scanResults.scores && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-16"
        >
          <div className="mb-8 flex items-center space-x-3">
            <Sparkles className="text-primary" size={28} />
            <h2 className="text-2xl font-bold">Profile Analysis Results</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(scanResults.scores).map(([platform, data]) => {
              if (data.status === "no profile detected") {
                return (
                  <div key={platform} className="bg-[#1e2128]/50 p-6 rounded-2xl border border-red-500/20 flex flex-col justify-between">
                    <div className="flex items-center space-x-3 mb-4">
                      {platform === 'github' ? <Terminal className="text-pink-400" size={24} /> : 
                       platform === 'leetcode' ? <Cpu className="text-yellow-500" size={24} /> : 
                       platform === 'linkedin' ? <Briefcase className="text-amber-600" size={24} /> : 
                       platform === 'portfolio' ? <Globe className="text-blue-400" size={24} /> : 
                       <FileText className="text-gray-400" size={24} />}
                      <h3 className="text-lg font-bold text-white capitalize">{platform}</h3>
                    </div>
                    <div className="flex items-center space-x-2 text-red-400 mt-2">
                      <XCircle size={18} />
                      <span className="font-semibold text-sm">no profile detected</span>
                    </div>
                  </div>
                );
              }

              return (
                <div key={platform} className="bg-[#1e2128] p-6 rounded-2xl border border-gray-800 flex flex-col relative overflow-hidden">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      {platform === 'github' ? <Terminal className="text-pink-400" size={24} /> : 
                       platform === 'leetcode' ? <Cpu className="text-yellow-500" size={24} /> : 
                       platform === 'linkedin' ? <Briefcase className="text-amber-600" size={24} /> : 
                       platform === 'portfolio' ? <Globe className="text-blue-400" size={24} /> : 
                       <FileText className="text-gray-400" size={24} />}
                      <h3 className="text-lg font-bold text-white capitalize">{platform}</h3>
                    </div>
                    {data.score > 0 && (
                      <div className="bg-primary/20 text-primary px-2 py-1 rounded text-xs font-bold">
                        Score: {data.score}
                      </div>
                    )}
                  </div>
                  
                  <div className="mb-4">
                    <span className="text-xs text-gray-500 uppercase tracking-widest">Username / Name</span>
                    <p className="text-white font-medium truncate">{data.username}</p>
                  </div>

                  {data.details && Object.keys(data.details).length > 0 && (
                    <div className="mt-auto pt-4 border-t border-gray-800 grid grid-cols-2 gap-3">
                      {Object.entries(data.details).map(([k, v]) => (
                        <div key={k} className="flex flex-col">
                          <span className="text-[10px] text-gray-500 uppercase block mb-0.5">{k}</span>
                          <span className="text-sm text-gray-300 font-semibold truncate" title={v}>{v !== null && v !== "" ? v : "N/A"}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
