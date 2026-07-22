import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getLinks, updateLinks, scanProfile, uploadResume } from '../services/api';
import { FileText, Globe, Briefcase, Terminal, Cpu, Loader2, Sparkles, GraduationCap, Code, BookOpen, ChevronRight, CheckCircle, XCircle } from 'lucide-react';

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

  useEffect(() => {
    getLinks().then(res => {
      setLinks(res.data);
    }).catch(err => {
      console.error("Using fallback local state due to backend error", err);
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

      {/* AI Recommendations */}
      {scanResults && scanResults.recommendations && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-16"
        >
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Sparkles className="text-primary" size={28} />
              <h2 className="text-2xl font-bold">AI Personalized Recommendations</h2>
            </div>
            {scanResults.recommendations.career_score !== undefined && (
              <div className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-full flex items-center space-x-2">
                <span className="text-gray-400 text-sm">Career Score:</span>
                <span className="text-white font-bold">{scanResults.recommendations.career_score}/100</span>
              </div>
            )}
          </div>

          {/* Skills Badges */}
          <div className="mb-10 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[#1e2128]/50 p-6 rounded-2xl border border-green-500/20">
              <div className="flex items-center space-x-2 mb-4 text-green-400">
                <CheckCircle size={20} />
                <h3 className="font-bold">Detected Skills</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {scanResults.recommendations.detected_skills?.length > 0 ? (
                  scanResults.recommendations.detected_skills.map((skill, idx) => (
                    <span key={idx} className="bg-green-500/10 text-green-400 border border-green-500/20 px-3 py-1 rounded-full text-xs font-semibold">
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-gray-500 text-sm">No specific skills detected.</span>
                )}
              </div>
            </div>

            <div className="bg-[#1e2128]/50 p-6 rounded-2xl border border-red-500/20">
              <div className="flex items-center space-x-2 mb-4 text-red-400">
                <XCircle size={20} />
                <h3 className="font-bold">Missing Core Skills</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {scanResults.recommendations.missing_skills?.length > 0 ? (
                  scanResults.recommendations.missing_skills.map((skill, idx) => (
                    <span key={idx} className="bg-red-500/10 text-red-400 border border-red-500/20 px-3 py-1 rounded-full text-xs font-semibold">
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-gray-500 text-sm">You have all core skills!</span>
                )}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Jobs Card */}
            <div className="bg-[#1e2128] p-6 rounded-2xl border border-gray-800">
              <div className="flex items-center space-x-3 mb-4 text-blue-400">
                <Briefcase size={24} />
                <h3 className="text-lg font-bold text-white">Recommended Jobs</h3>
              </div>
              <ul className="space-y-3">
                {scanResults.recommendations.jobs?.map((item, idx) => (
                  <li key={idx} className="flex items-start text-sm text-gray-300">
                    <ChevronRight size={16} className="text-blue-500 mr-2 flex-shrink-0 mt-0.5" />
                    <a href={getSearchUrl(item, 'jobs')} target="_blank" rel="noopener noreferrer" className="hover:text-white hover:underline transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Internships Card */}
            <div className="bg-[#1e2128] p-6 rounded-2xl border border-gray-800">
              <div className="flex items-center space-x-3 mb-4 text-purple-400">
                <GraduationCap size={24} />
                <h3 className="text-lg font-bold text-white">Internships</h3>
              </div>
              <ul className="space-y-3">
                {scanResults.recommendations.internships?.map((item, idx) => (
                  <li key={idx} className="flex items-start text-sm text-gray-300">
                    <ChevronRight size={16} className="text-purple-500 mr-2 flex-shrink-0 mt-0.5" />
                    <a href={getSearchUrl(item, 'internships')} target="_blank" rel="noopener noreferrer" className="hover:text-white hover:underline transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Hackathons Card */}
            <div className="bg-[#1e2128] p-6 rounded-2xl border border-gray-800">
              <div className="flex items-center space-x-3 mb-4 text-green-400">
                <Code size={24} />
                <h3 className="text-lg font-bold text-white">Hackathons</h3>
              </div>
              <ul className="space-y-3">
                {scanResults.recommendations.hackathons?.map((item, idx) => (
                  <li key={idx} className="flex items-start text-sm text-gray-300">
                    <ChevronRight size={16} className="text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <a href={getSearchUrl(item, 'hackathons')} target="_blank" rel="noopener noreferrer" className="hover:text-white hover:underline transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Workshops Card */}
            <div className="bg-[#1e2128] p-6 rounded-2xl border border-gray-800">
              <div className="flex items-center space-x-3 mb-4 text-orange-400">
                <BookOpen size={24} />
                <h3 className="text-lg font-bold text-white">Workshops to Attend</h3>
              </div>
              <ul className="space-y-3">
                {scanResults.recommendations.workshops?.map((item, idx) => (
                  <li key={idx} className="flex items-start text-sm text-gray-300">
                    <ChevronRight size={16} className="text-orange-500 mr-2 flex-shrink-0 mt-0.5" />
                    <a href={getSearchUrl(item, 'workshops')} target="_blank" rel="noopener noreferrer" className="hover:text-white hover:underline transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* LeetCode Card */}
            <div className="bg-[#1e2128] p-6 rounded-2xl border border-gray-800">
              <div className="flex items-center space-x-3 mb-4 text-yellow-500">
                <Terminal size={24} />
                <h3 className="text-lg font-bold text-white">LeetCode Practice</h3>
              </div>
              <ul className="space-y-3">
                {scanResults.recommendations.leetcode_problems?.map((item, idx) => (
                  <li key={idx} className="flex items-start text-sm text-gray-300">
                    <ChevronRight size={16} className="text-yellow-500 mr-2 flex-shrink-0 mt-0.5" />
                    <a href={getSearchUrl(item, 'leetcode_problems')} target="_blank" rel="noopener noreferrer" className="hover:text-white hover:underline transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
