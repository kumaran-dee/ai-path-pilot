import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  FileText, Link as LinkIcon, UploadCloud, Sparkles,
  CheckCircle, XCircle, Loader2, AlertCircle, ArrowRight,
  Lightbulb, BookOpen, Eye, X, Copy, Check, Terminal,
  User, Mail, Phone, MapPin, Code2, Award, GraduationCap,
  Briefcase, Star, BookMarked, Globe, ExternalLink, Download
} from 'lucide-react';
import { compareResumeToJob, uploadResume, getResumeDetails } from '../services/api';

// ── Set to false to strip dev features before final production release ──
const SHOW_DEV_FEATURES = false;

// ─────────────────────────────────────────────
// Syntax highlighter (pure regex, no deps)
// ─────────────────────────────────────────────
function syntaxHighlight(json) {
  if (!json) return '';
  if (typeof json !== 'string') json = JSON.stringify(json, undefined, 2);
  json = json
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  return json.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    (match) => {
      let cls = 'text-amber-400'; // number
      if (/^"/.test(match)) {
        cls = /:$/.test(match) ? 'text-sky-300 font-semibold' : 'text-emerald-400';
      } else if (/true|false/.test(match)) {
        cls = 'text-violet-400';
      } else if (/null/.test(match)) {
        cls = 'text-rose-400';
      }
      return `<span class="${cls}">${match}</span>`;
    }
  );
}

// ─────────────────────────────────────────────
// Structured Resume Viewer (card-based display)
// ─────────────────────────────────────────────
function Section({ icon: Icon, title, color, children }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="mb-5 rounded-2xl border border-gray-800 overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 bg-gray-900/80 hover:bg-gray-800/80 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Icon size={18} className={color} />
          <span className={`font-bold text-sm uppercase tracking-widest ${color}`}>{title}</span>
        </div>
        <span className="text-gray-500 text-xs">{open ? '▲ Collapse' : '▼ Expand'}</span>
      </button>
      {open && <div className="px-5 py-4 bg-[#0f1117]">{children}</div>}
    </div>
  );
}

function Chip({ text, color = 'bg-blue-900/50 text-blue-300 border-blue-800' }) {
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${color} mr-2 mb-2`}>
      {text}
    </span>
  );
}

function InfoRow({ label, value }) {
  if (!value || (Array.isArray(value) && !value.length)) return null;
  return (
    <div className="flex items-start gap-3 mb-2 text-sm">
      <span className="text-gray-500 w-36 flex-shrink-0">{label}</span>
      <span className="text-gray-200 break-words">{value}</span>
    </div>
  );
}

function StructuredResumeViewer({ data }) {
  if (!data) return null;

  // Flatten and map the new nested snake_case schema to the expected PascalCase structure for the UI
  const mappedData = {
    ResumeScore: data.resume_score ?? data.ResumeScore,
    CareerReadinessScore: data.career_readiness ?? data.CareerReadinessScore,
    FullName: data.personal_information?.full_name ?? data.FullName,
    CareerDomain: data.career_domain ?? data.CareerDomain,
    PreferredRoles: data.preferred_roles ?? data.PreferredRoles,
    YearsOfExperience: data.additional_metadata?.years_of_experience ?? data.YearsOfExperience,
    Location: data.contact_details?.location ?? data.Location,
    EmailAddress: data.contact_details?.email ?? data.EmailAddress,
    PhoneNumber: data.contact_details?.phone ?? data.PhoneNumber,
    LinkedInURL: data.contact_details?.linkedin ?? data.LinkedInURL,
    GitHubURL: data.contact_details?.github ?? data.GitHubURL,
    PortfolioURL: data.contact_details?.portfolio ?? data.PortfolioURL,
    TechnicalSkills: data.technical_skills ? Object.values(data.technical_skills).flat() : data.TechnicalSkills,
    Skills: data.skills ?? data.Skills,
    SoftSkills: data.soft_skills ?? data.SoftSkills,
    Languages: data.languages ?? data.Languages,
    Education: (data.education || data.Education || []).map(e => ({
      Degree: e.degree || e.Degree,
      FieldOfStudy: e.field_of_study || e.FieldOfStudy || '',
      Institution: e.institution || e.Institution,
      Year: e.year || e.Year,
      CGPA: e.cgpa || e.CGPA
    })),
    Experience: (data.experience || data.Experience || []).map(e => ({
      Title: e.role || e.Title,
      Company: e.company || e.Company,
      Duration: e.duration || e.Duration,
      Description: e.description || e.Description
    })),
    Projects: (data.projects || data.Projects || []).map(p => ({
      Title: p.name || p.Title,
      Link: p.link || p.Link,
      Description: p.description || p.Description,
      TechnologiesUsed: p.tech_stack || p.TechnologiesUsed
    })),
    Certifications: data.certifications ?? data.Certifications,
    Achievements: data.achievements ?? data.Achievements,
    Research: data.research ?? data.Research
  };

  data = mappedData;

  const scoreColor = (s) =>
    s >= 80 ? 'text-emerald-400' : s >= 60 ? 'text-yellow-400' : 'text-red-400';

  const linkVal = (url) =>
    url && url !== 'null' && url !== 'None' ? url : null;

  return (
    <div className="space-y-1">
      {/* Scores */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {[
          { label: 'Resume Score', value: data.ResumeScore ?? 0, suffix: '/100' },
          { label: 'Career Readiness', value: data.CareerReadinessScore ?? 0, suffix: '/100' },
        ].map(({ label, value, suffix }) => (
          <div key={label} className="bg-gray-900/80 rounded-2xl border border-gray-800 p-5 text-center">
            <div className={`text-5xl font-extrabold ${scoreColor(value)}`}>{value}<span className="text-lg text-gray-500 font-normal">{suffix}</span></div>
            <div className="text-xs text-gray-500 mt-2 uppercase tracking-widest">{label}</div>
          </div>
        ))}
      </div>

      {/* Personal Info */}
      <Section icon={User} title="Personal Information" color="text-sky-400">
        <InfoRow label="Full Name" value={data.FullName} />
        <InfoRow label="Career Domain" value={data.CareerDomain} />
        <InfoRow label="Preferred Roles" value={Array.isArray(data.PreferredRoles) ? data.PreferredRoles.join(', ') : data.PreferredRole} />
        <InfoRow label="Exp. (Years)" value={data.YearsOfExperience} />
        <InfoRow label="Location" value={data.Location} />
      </Section>

      {/* Contact */}
      <Section icon={Mail} title="Contact Details" color="text-violet-400">
        <InfoRow label="Email" value={data.EmailAddress} />
        <InfoRow label="Phone" value={data.PhoneNumber} />
        {linkVal(data.LinkedInURL) && (
          <div className="flex items-center gap-2 text-sm mb-2">
            <span className="text-gray-500 w-36">LinkedIn</span>
            <a href={data.LinkedInURL} target="_blank" rel="noreferrer" className="text-violet-400 hover:underline flex items-center gap-1">
              View Profile <ExternalLink size={12} />
            </a>
          </div>
        )}
        {linkVal(data.GitHubURL) && (
          <div className="flex items-center gap-2 text-sm mb-2">
            <span className="text-gray-500 w-36">GitHub</span>
            <a href={data.GitHubURL} target="_blank" rel="noreferrer" className="text-violet-400 hover:underline flex items-center gap-1">
              View Profile <ExternalLink size={12} />
            </a>
          </div>
        )}
        {linkVal(data.PortfolioURL) && (
          <div className="flex items-center gap-2 text-sm mb-2">
            <span className="text-gray-500 w-36">Portfolio</span>
            <a href={data.PortfolioURL} target="_blank" rel="noreferrer" className="text-violet-400 hover:underline flex items-center gap-1">
              View Portfolio <ExternalLink size={12} />
            </a>
          </div>
        )}
      </Section>

      {/* Skills */}
      <Section icon={Code2} title="Technical Skills" color="text-emerald-400">
        <div className="flex flex-wrap">
          {(data.TechnicalSkills || data.Skills || []).map((s, i) => (
            <Chip key={i} text={s} color="bg-emerald-900/40 text-emerald-300 border-emerald-800" />
          ))}
        </div>
      </Section>

      <Section icon={Star} title="Soft Skills" color="text-pink-400">
        <div className="flex flex-wrap">
          {(data.SoftSkills || []).map((s, i) => (
            <Chip key={i} text={s} color="bg-pink-900/40 text-pink-300 border-pink-800" />
          ))}
        </div>
      </Section>

      {(data.Languages || []).length > 0 && (
        <Section icon={Globe} title="Languages" color="text-cyan-400">
          <div className="flex flex-wrap">
            {data.Languages.map((l, i) => (
              <Chip key={i} text={l} color="bg-cyan-900/40 text-cyan-300 border-cyan-800" />
            ))}
          </div>
        </Section>
      )}

      {/* Education */}
      <Section icon={GraduationCap} title="Education" color="text-amber-400">
        {(data.Education || []).map((edu, i) => (
          <div key={i} className="mb-4 pl-3 border-l-2 border-amber-700">
            {typeof edu === 'string' ? (
              <p className="text-gray-300 text-sm">{edu}</p>
            ) : (
              <>
                <p className="font-semibold text-amber-300">{edu.Degree} — {edu.FieldOfStudy}</p>
                <p className="text-gray-400 text-sm">{edu.Institution}</p>
                <p className="text-gray-500 text-xs">{edu.Year} {edu.CGPA ? `• CGPA: ${edu.CGPA}` : ''}</p>
              </>
            )}
          </div>
        ))}
      </Section>

      {/* Experience */}
      {(data.Experience || []).length > 0 && (
        <Section icon={Briefcase} title="Experience" color="text-blue-400">
          {data.Experience.map((exp, i) => (
            <div key={i} className="mb-4 pl-3 border-l-2 border-blue-700">
              {typeof exp === 'string' ? (
                <p className="text-gray-300 text-sm">{exp}</p>
              ) : (
                <>
                  <p className="font-semibold text-blue-300">{exp.Title} @ {exp.Company}</p>
                  <p className="text-gray-500 text-xs mb-1">{exp.Duration}</p>
                  <p className="text-gray-400 text-sm">{exp.Description}</p>
                </>
              )}
            </div>
          ))}
        </Section>
      )}

      {/* Projects */}
      {(data.Projects || []).length > 0 && (
        <Section icon={Terminal} title="Projects" color="text-orange-400">
          {data.Projects.map((proj, i) => (
            <div key={i} className="mb-5 rounded-xl bg-gray-900/60 border border-gray-800 p-4">
              <div className="flex items-center justify-between mb-1">
                <p className="font-bold text-orange-300">{proj.Title}</p>
                {proj.Link && proj.Link !== 'null' && (
                  <a href={proj.Link} target="_blank" rel="noreferrer" className="text-orange-400 text-xs hover:underline flex items-center gap-1">
                    View <ExternalLink size={11} />
                  </a>
                )}
              </div>
              <p className="text-gray-400 text-sm mb-2">{proj.Description}</p>
              <div className="flex flex-wrap">
                {(proj.TechnologiesUsed || []).map((t, j) => (
                  <Chip key={j} text={t} color="bg-orange-900/30 text-orange-300 border-orange-800" />
                ))}
              </div>
            </div>
          ))}
        </Section>
      )}

      {/* Certifications */}
      {(data.Certifications || []).length > 0 && (
        <Section icon={Award} title="Certifications" color="text-yellow-400">
          <ul className="list-disc pl-4 space-y-1">
            {data.Certifications.map((c, i) => <li key={i} className="text-gray-300 text-sm">{c}</li>)}
          </ul>
        </Section>
      )}

      {/* Achievements */}
      {(data.Achievements || []).length > 0 && (
        <Section icon={Star} title="Achievements" color="text-rose-400">
          <ul className="list-disc pl-4 space-y-1">
            {data.Achievements.map((a, i) => <li key={i} className="text-gray-300 text-sm">{a}</li>)}
          </ul>
        </Section>
      )}

      {/* Research */}
      {(data.Research || []).length > 0 && (
        <Section icon={BookMarked} title="Research & Publications" color="text-teal-400">
          <ul className="list-disc pl-4 space-y-1">
            {data.Research.map((r, i) => <li key={i} className="text-gray-300 text-sm">{r}</li>)}
          </ul>
        </Section>
      )}

      {/* Interests */}
      {(data.Interests || []).length > 0 && (
        <Section icon={Sparkles} title="Interests" color="text-purple-400">
          <div className="flex flex-wrap">
            {data.Interests.map((interest, i) => (
              <Chip key={i} text={interest} color="bg-purple-900/40 text-purple-300 border-purple-800" />
            ))}
          </div>
        </Section>
      )}

      {/* Strengths & Weaknesses */}
      {((data.ResumeStrengths || []).length > 0 || (data.ResumeWeaknesses || []).length > 0) && (
        <Section icon={CheckCircle} title="AI Resume Analysis" color="text-green-400">
          {(data.ResumeStrengths || []).length > 0 && (
            <div className="mb-3">
              <p className="text-green-400 font-semibold text-xs uppercase tracking-widest mb-2">Strengths</p>
              <ul className="space-y-1">
                {data.ResumeStrengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-gray-300 text-sm">
                    <CheckCircle size={14} className="text-green-400 mt-0.5 flex-shrink-0" />{s}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {(data.ResumeWeaknesses || []).length > 0 && (
            <div>
              <p className="text-yellow-400 font-semibold text-xs uppercase tracking-widest mb-2">Areas to Improve</p>
              <ul className="space-y-1">
                {data.ResumeWeaknesses.map((w, i) => (
                  <li key={i} className="flex items-start gap-2 text-gray-300 text-sm">
                    <AlertCircle size={14} className="text-yellow-400 mt-0.5 flex-shrink-0" />{w}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Section>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────
// Main Compare Page
// ─────────────────────────────────────────────
export default function Compare() {
  const [jobLink, setJobLink] = useState('');
  const [jobLinkError, setJobLinkError] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [results, setResults] = useState(null);
  const [detailedResume, setDetailedResume] = useState(null);
  const [isFetchingDetails, setIsFetchingDetails] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(''); // status message during on-demand upload
  const [showModal, setShowModal] = useState(false);
  const [copied, setCopied] = useState(false);
  const [jsonView, setJsonView] = useState(false);
  const navigate = useNavigate();

  const STORAGE_KEY = 'ai_pilot_resume_profile';

  // ── Open the Detailed Resume inspector ──
  const handleViewDetails = async () => {
    setIsFetchingDetails(true);
    setUploadStatus('');
    try {
      // 1. Try localStorage first — check if it contains valid parsed data
      const cached = localStorage.getItem(STORAGE_KEY);
      if (cached) {
        try {
          const parsed = JSON.parse(cached);
          if (parsed && (parsed.FullName || parsed.personal_information?.full_name)) {
            setDetailedResume(parsed);
            setShowModal(true);
            return;
          }
        } catch (e) {
          localStorage.removeItem(STORAGE_KEY);
        }
      }

      // 2. Try backend DB (works if same Vercel invocation still alive)
      try {
        const res = await getResumeDetails();
        const profile = res.data.data;
        if (profile && (profile.FullName || profile.personal_information?.full_name)) {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
          setDetailedResume(profile);
          setShowModal(true);
          return;
        }
      } catch (_) {
        // DB empty / stateless — fall through
      }

      // 3. If a file is selected, upload it on-the-spot and show result
      if (resumeFile) {
        setUploadStatus('Extracting resume data with AI...');
        const fd = new FormData();
        fd.append('file', resumeFile);
        const res = await uploadResume(fd);
        const profile = res.data?.data;
        if (profile) {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
          setDetailedResume(profile);
          setShowModal(true);
          setUploadStatus('');
          return;
        }
        throw new Error('Empty response from server');
      }

      // 4. Nothing available — guide user
      alert('Please select your resume PDF/DOCX using the file picker first, then click \'Detailed Resume\'.');
    } catch (err) {
      console.error('Detailed Resume error:', err);
      setUploadStatus('');
      alert(`Failed to extract resume data: ${err.response?.data?.message || err.message}. Please try again.`);
    } finally {
      setIsFetchingDetails(false);
    }
  };

  const handleCopy = () => {
    if (detailedResume) {
      navigator.clipboard.writeText(JSON.stringify(detailedResume, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (detailedResume) {
      const blob = new Blob([JSON.stringify(detailedResume, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'detailed_resume_profile.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const validateJobLink = (url) => {
    if (!url || url.trim() === '') return '';
    try {
      const parsed = new URL(url);
      return (parsed.protocol !== 'https:' && parsed.protocol !== 'http:')
        ? 'Must be a valid http or https URL' : '';
    } catch {
      return 'Please enter a valid URL (e.g., https://...)';
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
      const data = res.data.data;
      setResults(data);
      if (data?.resume_profile) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data.resume_profile));
      }
    } catch (err) {
      console.error('Comparison failed:', err);
      const errorMsg = err.response?.data?.message || err.message || '';
      if (errorMsg.includes('Invalid job link')) {
        setJobLinkError('Invalid job link. The URL could not be reached.');
      } else {
        alert(`Failed to analyze the fit: ${errorMsg}. Make sure the backend is running.`);
      }
    } finally {
      setIsComparing(false);
    }
  };

  // Simple file picker — upload happens on-demand when Detailed Resume is clicked
  const onFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setResumeFile(file);
      // Clear any old cached profile when a new file is selected
      localStorage.removeItem(STORAGE_KEY);
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
        {/* Resume Column */}
        <div className="bg-[#1e2128] border border-gray-800 rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all hover:border-blue-500">
          <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mb-4">
            <FileText className="text-blue-400" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Your Resume</h2>
          <p className="text-gray-400 mb-6 text-sm">Upload your latest PDF or DOCX resume.</p>
          <label className="cursor-pointer w-full border-2 border-dashed border-gray-600 rounded-xl p-8 hover:bg-gray-800 transition-colors flex flex-col items-center">
            <UploadCloud size={32} className="text-gray-400 mb-3" />
            <span className="text-blue-400 font-semibold">{resumeFile ? resumeFile.name : 'Browse or Drag File'}</span>
            <input type="file" className="hidden" accept=".pdf,.doc,.docx" onChange={onFileChange} />
          </label>
          {resumeFile && (
            <p className="mt-3 text-xs text-blue-400 flex items-center gap-1">
              <CheckCircle size={12} /> File selected — click "Detailed Resume" to extract profile
            </p>
          )}
        </div>

        {/* Job Link Column */}
        <div className="bg-[#1e2128] border border-gray-800 rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all hover:border-purple-500">
          <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mb-4">
            <LinkIcon className="text-purple-400" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Job Link</h2>
          <p className="text-gray-400 mb-6 text-sm">Paste the URL of the job you want to apply for.</p>
          <div className="w-full">
            <input
              type="url"
              placeholder="e.g., https://linkedin.com/jobs/..."
              value={jobLink}
              onChange={(e) => { setJobLink(e.target.value); setJobLinkError(validateJobLink(e.target.value)); }}
              className={`w-full bg-gray-900 border ${jobLinkError ? 'border-red-500' : 'border-gray-700 focus:border-purple-500'} rounded-xl p-4 text-white focus:outline-none focus:ring-1 focus:ring-purple-500 transition-all text-center`}
            />
            {jobLinkError && <span className="text-red-400 text-xs mt-2 block">{jobLinkError}</span>}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center items-center flex-wrap gap-4">
        <button
          onClick={handleCompare}
          disabled={!resumeFile || !jobLink || !!jobLinkError || isComparing}
          className="flex items-center space-x-3 px-12 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-xl rounded-full shadow-lg disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 transition-transform"
        >
          {isComparing ? <Loader2 size={24} className="animate-spin" /> : <Sparkles size={24} />}
          <span>{isComparing ? 'Analyzing...' : 'Compare Fit'}</span>
        </button>

        {SHOW_DEV_FEATURES && (
          <button
            onClick={handleViewDetails}
            disabled={isFetchingDetails}
            className="flex items-center space-x-2 px-8 py-4 bg-gray-800 hover:bg-gray-700 text-white font-semibold text-lg rounded-full border border-gray-600 hover:scale-105 transition-transform shadow-md disabled:opacity-60 disabled:cursor-not-allowed"
            title="View AI-extracted resume profile (dev tool)"
          >
            {isFetchingDetails ? <Loader2 size={20} className="animate-spin" /> : <Eye size={20} />}
            <span>{isFetchingDetails ? (uploadStatus || 'Loading...') : 'Detailed Resume'}</span>
          </button>
        )}
      </div>

      {/* Upload status message */}
      {uploadStatus && (
        <div className="flex justify-center mt-4">
          <p className="flex items-center gap-2 text-sm text-blue-400 animate-pulse">
            <Loader2 size={14} className="animate-spin" /> {uploadStatus}
          </p>
        </div>
      )}

      {/* ── Match Results ── */}
      {results && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-16 bg-[#1e2128] border border-gray-800 rounded-3xl p-10 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-2 bg-gradient-to-b from-blue-500 to-purple-500 h-full" />

          <div className="flex flex-col md:flex-row items-center justify-between border-b border-gray-800 pb-8 mb-8">
            <div>
              <h2 className="text-3xl font-bold mb-2">AI Match Report</h2>
              <p className="text-gray-400">Here's how your resume stacks up against the job.</p>
            </div>
            <div className="mt-6 md:mt-0 flex space-x-8">
              {[
                { val: `${results.match_score}%`, label: 'Match Score', color: 'text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400' },
              ].map(({ val, label, color }) => (
                <div key={label} className="flex flex-col items-center">
                  <div className={`text-4xl font-extrabold ${color}`}>{val}</div>
                  <span className="text-xs text-gray-500 uppercase tracking-widest mt-1">{label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            <div>
              <h3 className="text-xl font-semibold mb-5 flex items-center text-green-400"><CheckCircle className="mr-2" /> Matched Skills</h3>
              <ul className="space-y-3">
                {results.matched_skills?.map((skill, idx) => (
                  <li key={idx} className="flex items-start bg-gray-900/50 p-4 rounded-xl border border-gray-800">
                    <CheckCircle size={20} className="text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300">{skill}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-5 flex items-center text-yellow-400"><AlertCircle className="mr-2" /> Missing Skills</h3>
              <ul className="space-y-3 mb-6">
                {results.missing_skills?.map((skill, idx) => (
                  <li key={idx} className="flex items-start bg-gray-900/50 p-4 rounded-xl border border-gray-800">
                    <XCircle size={20} className="text-yellow-500 mr-3 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300">{skill}</span>
                  </li>
                ))}
              </ul>
              {results.missing_skills?.length > 0 && (
                <div className="w-full py-3 bg-yellow-500/10 text-yellow-400 border border-yellow-500/30 rounded-xl flex items-center justify-center font-semibold">
                  Generate Learning Roadmap <ArrowRight className="ml-2" size={20} />
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mt-10">
            <div>
              <h3 className="text-xl font-semibold mb-5 flex items-center text-blue-400"><Lightbulb className="mr-2" /> Resume Improvements</h3>
              <ul className="space-y-3">
                {results.resume_improvements?.map((item, idx) => (
                  <li key={idx} className="flex items-start text-gray-300"><span className="text-blue-500 mr-2">•</span>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-5 flex items-center text-pink-400"><BookOpen className="mr-2" /> Recommended Courses</h3>
              <ul className="space-y-3">
                {results.recommended_courses?.map((course, idx) => (
                  <li key={idx} className="flex items-start text-gray-300"><span className="text-pink-500 mr-2">•</span>{course}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Should You Apply Banner */}
          <div className="mt-12 bg-gray-900/80 p-8 rounded-2xl border border-gray-700 flex flex-col md:flex-row items-center justify-between gap-6">
            {/* Left: Trophy icon */}
            <div className="flex-shrink-0 w-20 h-20 rounded-full border-4 border-yellow-500/60 bg-yellow-500/10 flex items-center justify-center text-4xl">
              ⭐
            </div>

            {/* Center: text */}
            <div className="flex-1 text-center">
              <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Should You Apply?</p>
              <div className={`text-4xl font-extrabold mb-3 ${
                results.should_apply === 'YES' ? 'text-green-400' :
                results.should_apply === 'MAYBE' ? 'text-yellow-400' :
                'text-red-400'
              }`}>
                {results.should_apply === 'YES' ? 'WORTH APPLYING' :
                 results.should_apply === 'MAYBE' ? 'WORTH APPLYING' :
                 'SKIP THIS ONE'}
              </div>
              <p className="text-gray-300 leading-relaxed max-w-xl mx-auto text-sm">{results.reason}</p>
            </div>

            {/* Right: Circular match score */}
            <div className="flex-shrink-0 flex flex-col items-center">
              <svg width="100" height="100" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="42" fill="none" stroke="#1f2937" strokeWidth="10"/>
                <circle
                  cx="50" cy="50" r="42" fill="none"
                  stroke={results.match_score >= 70 ? '#22c55e' : results.match_score >= 50 ? '#eab308' : '#ef4444'}
                  strokeWidth="10"
                  strokeDasharray={`${2 * Math.PI * 42}`}
                  strokeDashoffset={`${2 * Math.PI * 42 * (1 - (results.match_score || 0) / 100)}`}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                />
                <text x="50" y="46" textAnchor="middle" fill="white" fontSize="18" fontWeight="bold">{results.match_score}%</text>
                <text x="50" y="62" textAnchor="middle" fill="#9ca3af" fontSize="9">MATCH</text>
              </svg>
            </div>
          </div>
        </motion.div>
      )}

      {/* ── Developer Resume Viewer Modal ── */}
      <AnimatePresence>
        {showModal && SHOW_DEV_FEATURES && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.93, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.93 }}
              className="bg-[#13151c] border border-gray-700/80 rounded-3xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-5 border-b border-gray-800">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-blue-600/20 flex items-center justify-center">
                    <Eye size={18} className="text-blue-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-white">AI-Extracted Resume Profile</h2>
                    <p className="text-xs text-gray-500">Dev Tools · Exact data from your uploaded resume</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {/* Structured / Raw toggle */}
                  <button
                    onClick={() => setJsonView(v => !v)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
                  >
                    <Terminal size={13} />
                    {jsonView ? 'Structured View' : 'Raw JSON'}
                  </button>
                  <button
                    onClick={handleDownload}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
                  >
                    <Download size={13} />
                    Download JSON
                  </button>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
                  >
                    {copied ? <Check size={13} className="text-green-400" /> : <Copy size={13} />}
                    {copied ? 'Copied!' : 'Copy JSON'}
                  </button>
                  <button
                    onClick={() => setShowModal(false)}
                    className="p-2 rounded-lg border border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>

              {/* Modal Body */}
              <div className="flex-1 overflow-auto px-6 py-5">
                {!detailedResume ? (
                  <div className="flex flex-col items-center justify-center h-48 text-gray-500">
                    <AlertCircle size={36} className="mb-3 text-yellow-500" />
                    <p className="font-semibold">No extracted resume data found.</p>
                    <p className="text-sm mt-1">Please upload a resume first.</p>
                  </div>
                ) : jsonView ? (
                  /* Raw JSON view */
                  <div className="bg-gray-950 rounded-2xl border border-gray-800 p-5 overflow-auto">
                    <pre
                      className="text-sm font-mono whitespace-pre-wrap break-words leading-6"
                      dangerouslySetInnerHTML={{ __html: syntaxHighlight(detailedResume) }}
                    />
                  </div>
                ) : (
                  /* Structured card view */
                  <StructuredResumeViewer data={detailedResume} />
                )}
              </div>

              {/* Modal Footer */}
              <div className="px-6 py-4 border-t border-gray-800 flex items-center justify-between">
                <span className="text-xs text-gray-600">⚠ DEV TOOLS · Hidden in production (SHOW_DEV_FEATURES = false)</span>
                <button
                  onClick={() => setShowModal(false)}
                  className="px-5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-90 rounded-xl text-sm font-semibold text-white transition"
                >
                  Close Inspector
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
