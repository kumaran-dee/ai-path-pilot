import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { FileText, Link as LinkIcon, UploadCloud, Sparkles, CheckCircle, XCircle, Loader2, AlertCircle, ArrowRight, Lightbulb, BookOpen, User, Star, Eye, X } from 'lucide-react';
import { compareResumeToJob, getResumeDetails } from '../services/api';

export default function Compare() {
  const [jobLink, setJobLink] = useState('');
  const [jobLinkError, setJobLinkError] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [results, setResults] = useState(null);
  const [detailedResume, setDetailedResume] = useState(null);
  const [isFetchingDetails, setIsFetchingDetails] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const handleViewDetails = async () => {
    setIsFetchingDetails(true);
    try {
      const res = await getResumeDetails();
      setDetailedResume(res.data.data);
      setShowModal(true);
    } catch (err) {
      console.error(err);
      alert("No parsed resume found in the database. Please upload one first.");
    } finally {
      setIsFetchingDetails(false);
    }
  };

  const validateJobLink = (url) => {
    if (!url || url.trim() === '') return '';
    try {
      const parsed = new URL(url);
      if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
        return 'Must be a valid http or https URL';
      }
      return '';
    } catch (e) {
      return 'Please enter a valid URL (e.g., https://...)';
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
    }
  };

  const handleCompare = async () => {
    if (!resumeFile || !jobLink) return;
    setIsComparing(true);
    setResults(null);
    
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('jobLink', jobLink);
    
    try {
      const res = await compareResumeToJob(formData);
      setResults(res.data.data);
    } catch (err) {
      console.error("Comparison failed:", err);
      alert("Failed to analyze the fit. Make sure the backend is running.");
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-8 text-white max-w-6xl mx-auto"
    >
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold mb-3">Compare <span className="text-primary">Profile Match</span></h1>
        <p className="text-gray-400 text-lg">Upload your resume and drop a job link to see how well you match the role.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
        
        {/* Resume Grid Column */}
        <div className="bg-[#1e2128] border border-gray-800 rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all hover:border-blue-500 relative">
          <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mb-4">
            <FileText className="text-blue-400" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Your Resume</h2>
          <p className="text-gray-400 mb-6 text-sm">Upload your latest PDF or DOCX resume.</p>
          
          <div className="flex w-full space-x-4">
            <label className="cursor-pointer flex-1 border-2 border-dashed border-gray-600 rounded-xl p-8 hover:bg-gray-800 transition-colors flex flex-col items-center">
              <UploadCloud size={32} className="text-gray-400 mb-3" />
              <span className="text-blue-400 font-semibold">{resumeFile ? resumeFile.name : 'Browse or Drag File'}</span>
              <input type="file" className="hidden" accept=".pdf,.doc,.docx" onChange={handleFileChange} />
            </label>
          </div>
          <button 
            onClick={handleViewDetails}
            disabled={isFetchingDetails}
            className="mt-4 flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            {isFetchingDetails ? <Loader2 size={16} className="animate-spin" /> : <Eye size={16} />}
            <span>Detailed Resume (Testing)</span>
          </button>
        </div>

        {/* Job Link Grid Column */}
        <div className="bg-[#1e2128] border border-gray-800 rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all hover:border-purple-500 relative">
          <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mb-4">
            <LinkIcon className="text-purple-400" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Job Link</h2>
          <p className="text-gray-400 mb-6 text-sm">Paste the URL of the job you want to apply for.</p>
          
          <div className="w-full flex-1 flex flex-col justify-center">
            <input 
              type="url" 
              placeholder="e.g., https://linkedin.com/jobs/..." 
              value={jobLink}
              onChange={(e) => {
                const val = e.target.value;
                setJobLink(val);
                setJobLinkError(validateJobLink(val));
              }}
              className={`w-full bg-gray-900 border ${jobLinkError ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-gray-700 focus:border-purple-500 focus:ring-purple-500'} rounded-xl p-4 text-white focus:outline-none focus:ring-1 transition-all text-center mb-1`}
            />
            {jobLinkError && <span className="text-red-400 text-xs mt-2">{jobLinkError}</span>}
          </div>
        </div>

      </div>

      <div className="flex justify-center">
        <button 
          onClick={handleCompare}
          disabled={!resumeFile || !jobLink || !!jobLinkError || isComparing}
          className="flex items-center space-x-3 px-12 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-xl rounded-full shadow-lg disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 transition-transform"
        >
          {isComparing ? <Loader2 size={24} className="animate-spin" /> : <Sparkles size={24} />}
          <span>{isComparing ? 'Analyzing...' : 'Compare Fit'}</span>
        </button>
      </div>

      {results && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-16 bg-[#1e2128] border border-gray-800 rounded-3xl p-10 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-2 bg-gradient-to-b from-blue-500 to-purple-500 h-full"></div>
          
          <div className="flex flex-col md:flex-row items-center justify-between border-b border-gray-800 pb-8 mb-8">
            <div>
              <h2 className="text-3xl font-bold mb-2">AI Match Report</h2>
              <p className="text-gray-400">Here's how your resume stacks up against the job.</p>
            </div>
            <div className="mt-6 md:mt-0 flex space-x-8">
              <div className="flex flex-col items-center">
                <div className="text-4xl font-extrabold text-blue-400">{results.resume_score}</div>
                <span className="text-xs text-gray-500 uppercase tracking-widest mt-1">Resume Score</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="text-4xl font-extrabold text-pink-400">{results.career_readiness}</div>
                <span className="text-xs text-gray-500 uppercase tracking-widest mt-1">Career Readiness</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                  {results.match_score}%
                </div>
                <span className="text-xs text-gray-500 uppercase tracking-widest mt-1">Match Score</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            {/* Matched Skills */}
            <div>
              <h3 className="text-xl font-semibold mb-5 flex items-center text-green-400">
                <CheckCircle className="mr-2" /> Matched Skills
              </h3>
              <ul className="space-y-4">
                {results.matched_skills?.map((skill, idx) => (
                  <li key={idx} className="flex items-start bg-gray-900/50 p-4 rounded-xl border border-gray-800">
                    <CheckCircle size={20} className="text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300 leading-relaxed">{skill}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Missing Skills */}
            <div>
              <h3 className="text-xl font-semibold mb-5 flex items-center text-yellow-400">
                <AlertCircle className="mr-2" /> Missing Skills
              </h3>
              <ul className="space-y-4 mb-6">
                {results.missing_skills?.map((skill, idx) => (
                  <li key={idx} className="flex items-start bg-gray-900/50 p-4 rounded-xl border border-gray-800">
                    <XCircle size={20} className="text-yellow-500 mr-3 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300 leading-relaxed">{skill}</span>
                  </li>
                ))}
              </ul>
              {results.missing_skills && results.missing_skills.length > 0 && (
                <button 
                  onClick={() => navigate('/roadmap', { state: { missingSkills: results.missing_skills } })}
                  className="w-full py-3 bg-yellow-500/10 text-yellow-500 border border-yellow-500/30 hover:bg-yellow-500/20 rounded-xl flex items-center justify-center font-semibold transition-all"
                >
                  Generate Learning Roadmap <ArrowRight className="ml-2" size={20} />
                </button>
              )}
            </div>
          </div>

          {/* Improvements & Courses Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mt-10">
            <div>
              <h3 className="text-xl font-semibold mb-5 flex items-center text-blue-400">
                <Lightbulb className="mr-2" /> Resume Improvements
              </h3>
              <ul className="space-y-3">
                {results.resume_improvements?.map((item, idx) => (
                  <li key={idx} className="flex items-start text-gray-300">
                    <span className="text-blue-500 mr-2">•</span> {item}
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold mb-5 flex items-center text-pink-400">
                <BookOpen className="mr-2" /> Recommended Courses
              </h3>
              <ul className="space-y-3">
                {results.recommended_courses?.map((course, idx) => (
                  <li key={idx} className="flex items-start text-gray-300">
                    <span className="text-pink-500 mr-2">•</span> {course}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* AI Recommendation Verdict */}
          <div className="mt-12 bg-gray-900/80 p-8 rounded-2xl border border-gray-700 flex flex-col items-center text-center">
            <h3 className="text-lg font-bold text-gray-400 mb-2 uppercase tracking-widest">Should you apply?</h3>
            <div className={`text-4xl font-extrabold mb-4 ${
              results.should_apply === 'YES' ? 'text-green-400' : 
              results.should_apply === 'MAYBE' ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {results.should_apply}
            </div>
            <p className="text-gray-300 leading-relaxed max-w-3xl">{results.reason}</p>
          </div>
        </motion.div>
      )}

      {/* Detailed Resume Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-[#1e2128] border border-gray-700 rounded-2xl p-6 w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl relative"
          >
            <button 
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            >
              <X size={24} />
            </button>
            <h2 className="text-2xl font-bold mb-4 text-white flex items-center">
              <Eye className="mr-3 text-blue-400" /> Extracted Candidate Profile
            </h2>
            <p className="text-gray-400 text-sm mb-4">This is the raw internal profile the AI has extracted and saved into the SQLite database.</p>
            
            <div className="bg-gray-900 rounded-xl p-4 overflow-auto flex-1 border border-gray-800">
              <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap break-words">
                {JSON.stringify(detailedResume, null, 2)}
              </pre>
            </div>
            
          </motion.div>
        </div>
      )}

    </motion.div>
  );
}
