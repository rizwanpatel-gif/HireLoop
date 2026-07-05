import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { driver } from 'driver.js';
import 'driver.js/dist/driver.css';
import LoadingDuck from './LoadingDuck';
import TourBanner from '../onboarding/TourBanner';
import CopyButton from '../onboarding/CopyButton';
import { DEMO_RESUME_TEXT } from '../onboarding/tourSteps';
import { getStage, setStage, setTourCandidateName, markTourDone } from '../onboarding/tourStorage';
import { API_BASE_URL } from '../config';
import './CandidateForm.css';

const CandidateForm = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    job_role_id: '',
    resume_summary: ''
  });

  const [jobRoles, setJobRoles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [tourActive, setTourActive] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/job-roles/`)
      .then(res => res.ok ? res.json() : [])
      .then(data => setJobRoles(data))
      .catch(err => console.error('Error fetching job roles:', err));
  }, []);

  useEffect(() => {
    if (getStage() !== 'form') return;
    setTourActive(true);

    const driverObj = driver({
      showProgress: true,
      allowClose: true,
      popoverClass: 'hireloop-tour-popover',
      steps: [
        { element: '#name', popover: { title: 'Your name', description: 'Type your own real name here.' } },
        { element: '#email', popover: { title: 'Your real email', description: "Add your own real email - you'll actually receive the round/rejection emails, so you can see the system genuinely works." } },
        { element: '#job_role_id', popover: { title: 'Pick a role', description: 'Pick any role from the list.' } },
        { element: '#resume_summary', popover: { title: 'Paste a resume', description: "Use the \"Copy demo resume\" button above this field, then paste it in here." } },
        { element: '#submit-candidate-button', popover: { title: 'Submit', description: 'Once everything is filled in, click Submit to create the candidate and jump into the live chat.' } },
      ],
    });
    driverObj.drive();
    return () => driverObj.destroy();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage({ type: '', text: '' });

    try {
      const candidateData = {
        name: formData.name,
        email: formData.email,
        job_role_id: formData.job_role_id ? parseInt(formData.job_role_id, 10) : null,
        resume_summary: formData.resume_summary
      };

      const response = await fetch(`${API_BASE_URL}/api/candidates/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(candidateData)
      });

      if (response.ok) {
        const result = await response.json();

        if (result.status === 'rejected') {
          setIsSubmitting(false);
          const tourHint = tourActive ? ' Try picking a different role and submitting again.' : '';
          setMessage({
            type: 'error',
            text: `${result.message} (match score: ${result.match_score}/100)${tourHint}`
          });
        } else {
          if (tourActive) {
            setTourCandidateName(formData.name || 'them');
            setStage('chat:round1');
          }
          // Passed the AI screen and is now waiting on HR in chat - go there directly.
          navigate('/agent-chat');
        }
      } else {
        const error = await response.json();
        setIsSubmitting(false);
        setMessage({
          type: 'error',
          text: error.detail || 'Failed to create candidate'
        });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setIsSubmitting(false);
      setMessage({
        type: 'error',
        text: 'Network error. Please check if the backend server is running.'
      });
    }
  };

  return (
    <div className="candidate-form-container">
      {isSubmitting && <LoadingDuck message="Screening the resume..." />}
      <h2>Add New Candidate</h2>
      <p className="form-subtitle">
        Just the basics - the AI screens the resume against the role, and HireLoop's chat assistant handles everything from there.
      </p>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="candidate-form">
        <div className="form-group">
          <label htmlFor="name">Full Name *</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="Enter candidate's full name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">Email Address *</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="candidate@example.com"
          />
        </div>

        <div className="form-group">
          <label htmlFor="job_role_id">Applying For *</label>
          <select
            id="job_role_id"
            name="job_role_id"
            value={formData.job_role_id}
            onChange={handleChange}
            required
          >
            <option value="" disabled>Select a role...</option>
            {jobRoles.map(role => (
              <option key={role.id} value={role.id}>
                {role.title}{role.department ? ` (${role.department})` : ''}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <div className="form-label-row">
            <label htmlFor="resume_summary">Resume *</label>
            {tourActive && (
              <CopyButton text={DEMO_RESUME_TEXT} label="Copy demo resume" />
            )}
          </div>
          <textarea
            id="resume_summary"
            name="resume_summary"
            value={formData.resume_summary}
            onChange={handleChange}
            required
            rows="8"
            placeholder="Paste the candidate's resume text here..."
          ></textarea>
          <small>Experience and skills are extracted automatically from this text.</small>
        </div>

        <button
          id="submit-candidate-button"
          type="submit"
          className="submit-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Screening resume...' : 'Submit Candidate'}
        </button>
      </form>

      {tourActive && (
        <TourBanner
          instruction="Fill in your own name and email, pick any role, paste the demo resume, then submit."
          copyText={null}
          onSkip={() => { markTourDone(); setTourActive(false); }}
        />
      )}
    </div>
  );
};

export default CandidateForm;
