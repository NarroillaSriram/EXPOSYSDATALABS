import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import jsQR from 'jsqr';
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Search, 
  Download, 
  FileText, 
  Clock, 
  ExternalLink, 
  Trash2, 
  LogOut, 
  UploadCloud, 
  Grid, 
  Users, 
  Award,
  Link as LinkIcon
} from 'lucide-react';

const API_BASE = 'http://localhost:5001/api';
const UPLOADS_BASE = 'http://localhost:5001';

// ─── ADMIN LOGIN COMPONENT ──────────────────────────────────────────────────
function AdminLogin({ setToken }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/auth/login`, { email, password });
      localStorage.setItem('admin_token', res.data.token);
      localStorage.setItem('admin_name', res.data.admin.name);
      setToken(res.data.token);
      navigate('/admin/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid credentials or connection error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-darker px-4 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600 rounded-full filter blur-[120px] opacity-10 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-yellow-600 rounded-full filter blur-[120px] opacity-10 animate-pulse"></div>

      <div className="w-full max-w-md glass glass-glow rounded-2xl p-8 relative z-10">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-600/20 text-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-blue-500/30">
            <Shield className="w-8 h-8" />
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">Exposys Data Labs</h2>
          <p className="text-gray-400 mt-2 text-sm">Certificate Registry Admin Portal</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-200 text-sm p-3 rounded-lg mb-6 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-gray-300 text-xs font-semibold uppercase tracking-wider mb-2">Email Address</label>
            <input 
              type="email" 
              required
              className="w-full bg-brand-dark/60 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-sm"
              placeholder="admin@exposys.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-gray-300 text-xs font-semibold uppercase tracking-wider mb-2">Password</label>
            <input 
              type="password" 
              required
              className="w-full bg-brand-dark/60 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-sm"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-all duration-300 shadow-lg shadow-blue-600/30 hover:shadow-blue-600/40 text-sm flex items-center justify-center gap-2"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}

// ─── ADMIN DASHBOARD COMPONENT ──────────────────────────────────────────────
function AdminDashboard({ token, setToken }) {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showModal, setShowModal] = useState(false);
  
  // Date Fields for Approval Form
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [issueDate, setIssueDate] = useState(new Date().toISOString().split('T')[0]);
  const [actionLoading, setActionLoading] = useState(false);

  const navigate = useNavigate();

  const fetchStudents = async () => {
    try {
      const res = await axios.get(`${API_BASE}/students`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStudents(res.data);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        handleLogout();
      }
    }
  };

  useEffect(() => {
    if (!token) {
      navigate('/admin/login');
    } else {
      fetchStudents();
    }
  }, [token]);

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_name');
    setToken(null);
    navigate('/admin/login');
  };

  const handleActionClick = (student) => {
    setSelectedStudent(student);
    
    // Autofill start and end date based on duration
    const today = new Date();
    setIssueDate(today.toISOString().split('T')[0]);

    const start = new Date(today);
    let durationMonths = 1;
    if (student.duration) {
      const parsed = parseInt(student.duration);
      if (!isNaN(parsed)) durationMonths = parsed;
    }
    start.setMonth(start.getMonth() - durationMonths);

    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(today.toISOString().split('T')[0]);
    
    setShowModal(true);
  };

  const handleApprove = async () => {
    if (!startDate || !endDate || !issueDate) {
      alert('Please select all dates.');
      return;
    }
    setActionLoading(true);
    try {
      await axios.post(`${API_BASE}/certificates/approve`, {
        studentId: selectedStudent.id,
        startDate,
        endDate,
        issueDate,
        domainName: selectedStudent.internship_domain
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Certificate generated and stored on blockchain successfully!');
      setShowModal(false);
      fetchStudents();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to approve certificate.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!confirm('Are you sure you want to reject this certificate?')) return;
    setActionLoading(true);
    try {
      await axios.post(`${API_BASE}/certificates/reject`, {
        studentId: selectedStudent.id,
        studentName: selectedStudent.name,
        domainName: selectedStudent.internship_domain
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Application marked as Rejected.');
      setShowModal(false);
      fetchStudents();
    } catch (err) {
      alert('Error: ' + (err.response?.data?.error || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  const handleHold = async () => {
    setActionLoading(true);
    try {
      await axios.post(`${API_BASE}/certificates/hold`, {
        studentId: selectedStudent.id,
        studentName: selectedStudent.name,
        domainName: selectedStudent.internship_domain
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Application placed on hold.');
      setShowModal(false);
      fetchStudents();
    } catch (err) {
      alert('Error: ' + (err.response?.data?.error || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  const handleRevoke = async (certificateId) => {
    if (!confirm('WARNING: Revoking a certificate will update its record on blockchain. This action is irreversible! Are you sure?')) return;
    setActionLoading(true);
    try {
      await axios.post(`${API_BASE}/certificates/revoke`, { certificateId }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Certificate successfully revoked on blockchain.');
      setShowModal(false);
      fetchStudents();
    } catch (err) {
      alert('Revocation failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  // Filter Logic
  const filteredStudents = students.filter(student => {
    const term = search.toLowerCase();
    const nameMatch = student.name.toLowerCase().includes(term) || student.email.toLowerCase().includes(term);
    const domainMatch = domainFilter === '' || student.internship_domain === domainFilter;
    return nameMatch && domainMatch;
  });

  const domains = [...new Set(students.map(s => s.internship_domain).filter(Boolean))];

  // Stats Counters
  const totalStudents = students.length;
  const approvedCount = students.filter(s => s.certificate_status === 'approved').length;
  const pendingCount = students.filter(s => !s.certificate_status || s.certificate_status === 'held').length;
  const revokedCount = students.filter(s => s.certificate_status === 'revoked').length;

  return (
    <div className="min-h-screen bg-brand-darker text-white">
      {/* Navbar */}
      <nav className="bg-brand-dark border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600/10 text-blue-500 w-10 h-10 rounded-xl flex items-center justify-center border border-blue-500/20">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">Exposys Data Labs</h1>
            <p className="text-xs text-gray-400">Blockchain Certificate Console</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400 hidden sm:inline">Signed in as: <strong className="text-white">{localStorage.getItem('admin_name')}</strong></span>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white px-4 py-2 rounded-xl transition text-sm font-medium"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto p-6 md:p-8 space-y-8">
        
        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          <div className="glass rounded-2xl p-5 border-l-4 border-blue-500">
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Total Students</p>
            <h3 className="text-3xl font-extrabold mt-2">{totalStudents}</h3>
          </div>
          <div className="glass rounded-2xl p-5 border-l-4 border-green-500">
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Approved Certificates</p>
            <h3 className="text-3xl font-extrabold mt-2 text-green-400">{approvedCount}</h3>
          </div>
          <div className="glass rounded-2xl p-5 border-l-4 border-yellow-500">
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Pending / On Hold</p>
            <h3 className="text-3xl font-extrabold mt-2 text-yellow-400">{pendingCount}</h3>
          </div>
          <div className="glass rounded-2xl p-5 border-l-4 border-red-500">
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Revoked</p>
            <h3 className="text-3xl font-extrabold mt-2 text-red-400">{revokedCount}</h3>
          </div>
        </div>

        {/* Filters and List */}
        <div className="glass rounded-2xl p-6 space-y-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <h2 className="text-lg font-bold tracking-tight">Internship Records</h2>
            
            <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
              {/* Search */}
              <div className="relative flex-1 sm:flex-initial">
                <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3.5" />
                <input 
                  type="text"
                  placeholder="Search name or email..."
                  className="bg-brand-dark/70 border border-gray-700 rounded-xl pl-9 pr-4 py-2.5 text-sm w-full focus:outline-none focus:border-blue-500 text-white"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>

              {/* Domain filter */}
              <select
                className="bg-brand-dark border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-gray-300 focus:outline-none focus:border-blue-500"
                value={domainFilter}
                onChange={(e) => setDomainFilter(e.target.value)}
              >
                <option value="">All Domains</option>
                {domains.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Student Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400">
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-xs">Student</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-xs">Internship Domain</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-xs">Duration</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-xs">Verification Status</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-xs text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/50">
                {filteredStudents.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="py-8 text-center text-gray-500">No student records found.</td>
                  </tr>
                ) : (
                  filteredStudents.map(student => (
                    <tr key={student.id} className="hover:bg-brand-navy/20 transition-all">
                      <td className="py-4 px-4">
                        <div className="font-semibold text-white">{student.name}</div>
                        <div className="text-gray-400 text-xs">{student.email}</div>
                      </td>
                      <td className="py-4 px-4 font-medium text-gray-300">{student.internship_domain}</td>
                      <td className="py-4 px-4 text-gray-400">{student.duration || 'N/A'}</td>
                      <td className="py-4 px-4">
                        {student.certificate_status === 'approved' && (
                          <span className="inline-flex items-center gap-1 bg-green-500/10 border border-green-500/20 text-green-400 text-xs px-2.5 py-1 rounded-full font-medium">
                            <CheckCircle className="w-3.5 h-3.5" /> Approved
                          </span>
                        )}
                        {student.certificate_status === 'rejected' && (
                          <span className="inline-flex items-center gap-1 bg-red-500/10 border border-red-500/20 text-red-400 text-xs px-2.5 py-1 rounded-full font-medium">
                            <XCircle className="w-3.5 h-3.5" /> Rejected
                          </span>
                        )}
                        {student.certificate_status === 'held' && (
                          <span className="inline-flex items-center gap-1 bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs px-2.5 py-1 rounded-full font-medium">
                            <Clock className="w-3.5 h-3.5" /> On Hold
                          </span>
                        )}
                        {student.certificate_status === 'revoked' && (
                          <span className="inline-flex items-center gap-1 bg-orange-500/15 border border-orange-500/30 text-orange-400 text-xs px-2.5 py-1 rounded-full font-medium">
                            <AlertTriangle className="w-3.5 h-3.5" /> Revoked
                          </span>
                        )}
                        {!student.certificate_status && (
                          <span className="inline-flex items-center gap-1 bg-gray-500/10 border border-gray-500/20 text-gray-400 text-xs px-2.5 py-1 rounded-full font-medium">
                            Pending Approval
                          </span>
                        )}
                      </td>
                      <td className="py-4 px-4 text-right">
                        <button
                          onClick={() => handleActionClick(student)}
                          className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3.5 py-1.5 rounded-lg transition font-semibold"
                        >
                          Manage
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Approve/Revoke Modal */}
      {showModal && selectedStudent && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="w-full max-w-2xl bg-brand-navy rounded-2xl p-6 border border-gray-800 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-gray-800 pb-4">
              <div>
                <h3 className="text-xl font-bold text-white">Certificate Management</h3>
                <p className="text-xs text-gray-400 mt-1">Configure status for {selectedStudent.name}</p>
              </div>
              <button 
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white transition text-lg"
              >
                &times;
              </button>
            </div>

            {/* Current Certificate Info (if approved) */}
            {selectedStudent.certificate_status === 'approved' && (
              <div className="bg-green-500/5 border border-green-500/10 rounded-xl p-4 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-green-400">Blockchain Record Info</h4>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-gray-400">Certificate ID:</span>
                    <p className="font-mono text-white mt-0.5">{selectedStudent.certificate_id}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Blockchain Hash:</span>
                    <p className="font-mono text-white mt-0.5 truncate" title={selectedStudent.blockchain_hash}>{selectedStudent.blockchain_hash}</p>
                  </div>
                  <div className="col-span-2">
                    <span className="text-gray-400">Transaction Proof:</span>
                    <p className="font-mono text-blue-400 mt-0.5 flex items-center gap-1 break-all">
                      <a href={`https://amoy.polygonscan.com/tx/${selectedStudent.tx_hash}`} target="_blank" rel="noreferrer" className="hover:underline flex items-center gap-1">
                        {selectedStudent.tx_hash} <ExternalLink className="w-3.5 h-3.5 inline" />
                      </a>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <a 
                    href={`${UPLOADS_BASE}${selectedStudent.pdf_path}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2.5 rounded-xl transition text-center text-xs font-semibold flex items-center justify-center gap-2"
                  >
                    <FileText className="w-4 h-4" /> Download Certificate PDF
                  </a>
                  <button 
                    onClick={() => handleRevoke(selectedStudent.certificate_id)}
                    disabled={actionLoading}
                    className="flex-1 bg-red-950 hover:bg-red-900 border border-red-800 text-red-300 py-2.5 rounded-xl transition text-xs font-semibold flex items-center justify-center gap-2"
                  >
                    <AlertTriangle className="w-4 h-4" /> Revoke Certificate
                  </button>
                </div>
              </div>
            )}

            {selectedStudent.certificate_status === 'revoked' && (
              <div className="bg-red-500/5 border border-red-500/10 rounded-xl p-4 space-y-1 text-center">
                <AlertTriangle className="w-8 h-8 text-orange-500 mx-auto mb-2" />
                <h4 className="text-sm font-bold text-orange-400">This Certificate Has Been Officially Revoked</h4>
                <p className="text-xs text-gray-400">The record has been updated on the blockchain register to indicate invalid status.</p>
              </div>
            )}

            {/* Config Form for Pending, Held, or Re-approving */}
            {selectedStudent.certificate_status !== 'approved' && selectedStudent.certificate_status !== 'revoked' && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Start Date</label>
                    <input 
                      type="date"
                      className="bg-brand-dark/70 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 w-full"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">End Date</label>
                    <input 
                      type="date"
                      className="bg-brand-dark/70 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 w-full"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Issue Date</label>
                    <input 
                      type="date"
                      className="bg-brand-dark/70 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 w-full"
                      value={issueDate}
                      onChange={(e) => setIssueDate(e.target.value)}
                    />
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-800">
                  <button
                    onClick={handleApprove}
                    disabled={actionLoading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition text-sm flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20"
                  >
                    {actionLoading ? 'Deploying...' : 'Approve & Issue Certificate'}
                  </button>
                  <button
                    onClick={handleHold}
                    disabled={actionLoading}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-3 px-6 rounded-xl transition text-sm"
                  >
                    Put On Hold
                  </button>
                  <button
                    onClick={handleReject}
                    disabled={actionLoading}
                    className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-xl transition text-sm"
                  >
                    Reject
                  </button>
                </div>
              </div>
            )}
            
            <div className="flex justify-end pt-2">
              <button 
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white text-xs font-medium uppercase tracking-wider transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── PUBLIC VERIFICATION PAGE ───────────────────────────────────────────────
function PublicVerify() {
  const { id } = useParams();
  const [certId, setCertId] = useState(id || '');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [uploadName, setUploadName] = useState('');

  const runVerification = async (searchId) => {
    if (!searchId.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await axios.get(`${API_BASE}/certificates/verify/${searchId.trim()}`);
      setResult(res.data);
    } catch (err) {
      setError('Verification service offline or network issue');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      runVerification(id);
    }
  }, [id]);

  const handleQRUpload = (e) => {
    const file = e.target.files[0];
    if (!file) {
      setUploadName('');
      return;
    }
    setUploadName(file.name);

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        context.drawImage(img, 0, 0, img.width, img.height);
        
        try {
          const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
          const code = jsQR(imageData.data, imageData.width, imageData.height);
          
          if (code) {
            const qrText = code.data;
            const match = qrText.match(/EXPOSYS-[A-Z]+-\d+-\d+/);
            if (match) {
              setCertId(match[0]);
              runVerification(match[0]);
            } else {
              alert(`QR code scanned successfully, but no valid Exposys Certificate ID was found in it.\\n\\nQR Data: ${qrText}`);
            }
          } else {
            alert("Could not detect any QR code in the uploaded image. Please ensure the image is clear and contains a QR code.");
          }
        } catch (err) {
          console.error(err);
          alert("Error processing the image.");
        }
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="min-h-screen bg-brand-darker text-white p-6 relative overflow-hidden flex flex-col items-center justify-center">
      {/* Abstract Background Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600 rounded-full filter blur-[120px] opacity-10 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-yellow-600 rounded-full filter blur-[120px] opacity-10 animate-pulse"></div>

      <div className="w-full max-w-3xl space-y-8 relative z-10 my-10">
        
        {/* Branding & Header */}
        <div className="text-center">
          <div className="bg-blue-600/10 text-blue-500 w-14 h-14 rounded-2xl flex items-center justify-center border border-blue-500/20 mx-auto mb-4">
            <Shield className="w-7 h-7" />
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Exposys Data Labs</h1>
          <p className="text-gray-400 mt-2">Internship Certificate Verification Protocol</p>
        </div>

        {/* Verification Inputs */}
        <div className="glass rounded-2xl p-6 md:p-8 space-y-6">
          <h2 className="text-lg font-bold text-gray-200">Verify Credentials</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Input Box ID */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">Search by Certificate ID</label>
              <div className="relative">
                <input 
                  type="text"
                  placeholder="EXPOSYS-CERT-3-XXXX"
                  className="w-full bg-brand-dark/70 border border-gray-700 rounded-xl pl-4 pr-10 py-3 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-white"
                  value={certId}
                  onChange={(e) => setCertId(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && runVerification(certId)}
                />
                <button 
                  onClick={() => runVerification(certId)}
                  className="absolute right-2 top-2 p-1.5 text-blue-500 hover:text-blue-400 rounded-lg hover:bg-gray-800 transition"
                >
                  <Search className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* QR Scan Upload */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">Verify by QR Code Image</label>
              <label className="flex items-center gap-3 w-full bg-brand-dark/70 border border-dashed border-gray-700 hover:border-blue-500 rounded-xl px-4 py-3 cursor-pointer transition-all">
                <UploadCloud className="w-5 h-5 text-gray-500 shrink-0" />
                <span className={uploadName ? "text-blue-400 text-sm truncate font-medium" : "text-gray-400 text-sm truncate"}>
                  {uploadName ? `Scanning: ${uploadName}...` : 'Upload QR Code image...'}
                </span>
                <input 
                  type="file" 
                  accept="image/*"
                  className="hidden" 
                  onChange={handleQRUpload}
                />
              </label>
            </div>

          </div>
        </div>

        {/* Loading Indicator */}
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-400 text-xs mt-3">Interrogating Polygon blockchain registry...</p>
          </div>
        )}

        {/* Error Details */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-200 text-sm p-4 rounded-xl flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Verification Result Card */}
        {result && (
          <div className={`glass rounded-2xl p-6 md:p-8 border-t-4 transition-all duration-500 shadow-xl ${
            result.status === 'valid' ? 'border-t-green-500 shadow-green-500/5' : 
            result.status === 'revoked' ? 'border-t-orange-500 shadow-orange-500/5' : 
            'border-t-red-500 shadow-red-500/5'
          }`}>
            
            {/* Status Header */}
            <div className="flex flex-col sm:flex-row items-center sm:justify-between gap-4 border-b border-gray-800 pb-5 mb-5">
              <div className="flex items-center gap-3">
                {result.status === 'valid' && (
                  <>
                    <CheckCircle className="w-10 h-10 text-green-500" />
                    <div>
                      <h3 className="text-xl font-bold text-green-400">✅ Valid Certificate</h3>
                      <p className="text-xs text-gray-400 mt-0.5">Integrity cryptographically verified on-chain</p>
                    </div>
                  </>
                )}
                {result.status === 'revoked' && (
                  <>
                    <AlertTriangle className="w-10 h-10 text-orange-500 animate-bounce" />
                    <div>
                      <h3 className="text-xl font-bold text-orange-400">⚠ Revoked Certificate</h3>
                      <p className="text-xs text-gray-400 mt-0.5">This certificate has been revoked by admin</p>
                    </div>
                  </>
                )}
                {result.status === 'rejected' && (
                  <>
                    <XCircle className="w-10 h-10 text-red-500" />
                    <div>
                      <h3 className="text-xl font-bold text-red-400">❌ Rejected Application</h3>
                      <p className="text-xs text-gray-400 mt-0.5">This certificate application was rejected</p>
                    </div>
                  </>
                )}
                {result.status === 'held' && (
                  <>
                    <Clock className="w-10 h-10 text-yellow-500" />
                    <div>
                      <h3 className="text-xl font-bold text-yellow-400">⚠ Verification Pending</h3>
                      <p className="text-xs text-gray-400 mt-0.5">This certificate is currently on hold</p>
                    </div>
                  </>
                )}
                {result.status === 'invalid' && (
                  <>
                    <XCircle className="w-10 h-10 text-red-500" />
                    <div>
                      <h3 className="text-xl font-bold text-red-400">❌ Invalid Certificate</h3>
                      <p className="text-xs text-gray-400 mt-0.5">No certificate matches this identifier</p>
                    </div>
                  </>
                )}
              </div>

              {result.status === 'valid' && result.certificate?.pdf_path && (
                <a 
                  href={`${UPLOADS_BASE}${result.certificate.pdf_path}`}
                  target="_blank"
                  rel="noreferrer"
                  className="bg-green-600 hover:bg-green-700 text-white text-xs font-bold px-4 py-2 rounded-xl transition flex items-center gap-2 shadow-lg shadow-green-600/20 w-full sm:w-auto justify-center"
                >
                  <Download className="w-4 h-4" /> Download PDF
                </a>
              )}
            </div>

            {/* Certificate Details */}
            {result.certificate && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                  <div className="bg-brand-dark/40 rounded-xl p-3.5 border border-gray-800">
                    <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider block">Student Name</span>
                    <strong className="text-white text-base mt-1 block">{result.certificate.student_name}</strong>
                  </div>
                  <div className="bg-brand-dark/40 rounded-xl p-3.5 border border-gray-800">
                    <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider block">Internship Domain</span>
                    <strong className="text-white text-base mt-1 block">{result.certificate.domain_name}</strong>
                  </div>
                  <div className="bg-brand-dark/40 rounded-xl p-3.5 border border-gray-800">
                    <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider block">Duration</span>
                    <strong className="text-gray-300 mt-1 block">
                      {new Date(result.certificate.start_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })} to {new Date(result.certificate.end_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </strong>
                  </div>
                  <div className="bg-brand-dark/40 rounded-xl p-3.5 border border-gray-800">
                    <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider block">Issue Date</span>
                    <strong className="text-gray-300 mt-1 block">
                      {new Date(result.certificate.issue_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </strong>
                  </div>
                </div>

                {/* Blockchain Proofs */}
                {result.blockchain && (
                  <div className="space-y-3 pt-4 border-t border-gray-800/80 text-xs">
                    <h4 className="text-gray-400 font-bold uppercase tracking-wider">Cryptographic Proof</h4>
                    
                    <div className="bg-brand-dark/50 rounded-xl p-4 space-y-3 font-mono border border-gray-800">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-1">
                        <span className="text-gray-400 w-36 shrink-0 font-sans">Certificate Hash:</span>
                        <span className="text-gray-300 select-all break-all">{result.blockchain.hash}</span>
                      </div>
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-1">
                        <span className="text-gray-400 w-36 shrink-0 font-sans">Blockchain Network:</span>
                        <span className="text-gray-300 font-sans">Polygon Network {result.blockchain.isMock ? '(Local EVM Testbed)' : '(Public Mainnet)'}</span>
                      </div>
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-1">
                        <span className="text-gray-400 w-36 shrink-0 font-sans">Transaction Hash:</span>
                        <span className="text-blue-400 select-all break-all flex items-center gap-1">
                          <a href={`https://amoy.polygonscan.com/tx/${result.blockchain.txHash}`} target="_blank" rel="noreferrer" className="hover:underline flex items-center gap-1">
                            {result.blockchain.txHash} <ExternalLink className="w-3 h-3" />
                          </a>
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer links */}
      <div className="mt-8 flex gap-4 text-xs text-gray-500 z-10">
        <Link to="/download" className="hover:text-blue-400 transition">Student Download Hub</Link>
      </div>
    </div>
  );
}

// ─── STUDENT DOWNLOAD PORTAL ────────────────────────────────────────────────
function StudentDownload() {
  const [search, setSearch] = useState('');
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!search.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await axios.get(`${API_BASE}/certificates/download-search?search=${encodeURIComponent(search.trim())}`);
      setResults(res.data);
    } catch (err) {
      alert("Error searching database.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-darker text-white p-6 flex flex-col items-center justify-center relative overflow-hidden">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600 rounded-full filter blur-[120px] opacity-10 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-yellow-600 rounded-full filter blur-[120px] opacity-10 animate-pulse"></div>

      <div className="w-full max-w-3xl space-y-8 relative z-10 my-10">
        
        {/* Header */}
        <div className="text-center">
          <div className="bg-blue-600/10 text-blue-500 w-14 h-14 rounded-2xl flex items-center justify-center border border-blue-500/20 mx-auto mb-4">
            <Download className="w-7 h-7" />
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Student Certificate Hub</h1>
          <p className="text-gray-400 mt-2 font-medium">Download your officially registered Exposys Internship Certificate</p>
        </div>

        {/* Search form */}
        <div className="glass rounded-2xl p-6 md:p-8">
          <form onSubmit={handleSearch} className="space-y-4">
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">Search by Registered Email or Name</label>
            <div className="flex flex-col sm:flex-row gap-3">
              <input 
                type="text"
                placeholder="Enter email or student name..."
                required
                className="flex-1 bg-brand-dark/70 border border-gray-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500 text-white"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <button 
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl transition text-sm font-bold flex items-center justify-center gap-2 shrink-0"
              >
                {loading ? 'Searching...' : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>Search Records</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {searched && !loading && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Found {results.length} record(s)</h3>

            {results.length === 0 ? (
              <div className="glass rounded-2xl p-6 text-center text-gray-500">
                No approved certificate found matching your request. Make sure your admin has approved and issued the certificate.
              </div>
            ) : (
              results.map(cert => (
                <div key={cert.certificate_id} className="glass rounded-2xl p-6 border-l-4 border-l-blue-500 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:border-l-blue-400 transition-all">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-base font-bold text-white">{cert.student_name}</h4>
                      {cert.status === 'revoked' ? (
                        <span className="bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] px-2 py-0.5 rounded font-semibold uppercase tracking-wider">Revoked</span>
                      ) : (
                        <span className="bg-green-500/10 border border-green-500/20 text-green-400 text-[10px] px-2 py-0.5 rounded font-semibold uppercase tracking-wider">Approved</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-300 mt-1 font-medium">{cert.domain_name} ({cert.email})</p>
                    <p className="text-xs text-gray-400 mt-1 font-mono">ID: {cert.certificate_id}</p>
                  </div>

                  {cert.status === 'approved' && cert.pdf_path && (
                    <a 
                      href={`${UPLOADS_BASE}${cert.pdf_path}`}
                      target="_blank"
                      rel="noreferrer"
                      className="bg-green-600 hover:bg-green-700 text-white text-xs font-bold px-4 py-3 rounded-xl transition flex items-center gap-2 shrink-0 shadow-lg shadow-green-600/15 w-full sm:w-auto justify-center"
                    >
                      <Download className="w-4 h-4" /> Download Certificate
                    </a>
                  )}
                  {cert.status === 'revoked' && (
                    <div className="text-orange-400 text-xs flex items-center gap-1.5 font-semibold bg-orange-500/5 px-3 py-2 border border-orange-500/20 rounded-xl">
                      <AlertTriangle className="w-4 h-4" /> Wthheld / Revoked
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Footer links */}
      <div className="mt-8 flex gap-4 text-xs text-gray-500 z-10">
        <Link to="/verify" className="hover:text-blue-400 transition">Verification Center</Link>
      </div>
    </div>
  );
}

// ─── MAIN ROUTER COMPONENT ──────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(localStorage.getItem('admin_token') || null);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<PublicVerify />} />
        <Route path="/verify" element={<PublicVerify />} />
        <Route path="/verify/:id" element={<PublicVerify />} />
        <Route path="/download" element={<StudentDownload />} />
        <Route path="/admin/login" element={<AdminLogin setToken={setToken} />} />
        <Route path="/admin/dashboard" element={<AdminDashboard token={token} setToken={setToken} />} />
      </Routes>
    </Router>
  );
}
