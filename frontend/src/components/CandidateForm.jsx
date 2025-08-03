import React, { useState } from 'react';
import './CandidateForm.css';

const CandidateForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    current_title: '',
    skills: '',
    resume_summary: '',
    preferred_interview_date: '',
    phone: '',
    location: '',
    experience_years: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage({ type: '', text: '' });

    try {
      // Prepare data
      const candidateData = {
        ...formData,
        skills: formData.skills.split(',').map(skill => skill.trim()).filter(skill => skill),
        experience_years: formData.experience_years ? parseFloat(formData.experience_years) : null,
        preferred_interview_date: formData.preferred_interview_date ? 
          new Date(formData.preferred_interview_date).toISOString() : null
      };

      console.log('Submitting candidate data:', candidateData);

      // Submit to API
      const response = await fetch('http://localhost:8000/api/candidates/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(candidateData)
      });

      if (response.ok) {
        const result = await response.json();
        setMessage({ 
          type: 'success', 
          text: `Candidate ${result.name} created successfully! ID: ${result.id}` 
        });
        
        // Reset form
        setFormData({
          name: '',
          email: '',
          current_title: '',
          skills: '',
          resume_summary: '',
          preferred_interview_date: '',
          phone: '',
          location: '',
          experience_years: ''
        });
      } else {
        const error = await response.json();
        setMessage({ 
          type: 'error', 
          text: error.detail || 'Failed to create candidate' 
        });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setMessage({ 
        type: 'error', 
        text: 'Network error. Please check if the backend server is running.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="candidate-form-container">
      <h2>Add New Candidate</h2>
      
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
          <label htmlFor="current_title">Current Job Title *</label>
          <input
            type="text"
            id="current_title"
            name="current_title"
            value={formData.current_title}
            onChange={handleChange}
            required
            placeholder="e.g., Senior Software Engineer"
          />
        </div>

        <div className="form-group">
          <label htmlFor="skills">Technical Skills *</label>
          <input
            type="text"
            id="skills"
            name="skills"
            value={formData.skills}
            onChange={handleChange}
            required
            placeholder="React, Node.js, Python, AWS (comma-separated)"
          />
          <small>Separate skills with commas</small>
        </div>

        <div className="form-group">
          <label htmlFor="resume_summary">Resume Summary *</label>
          <textarea
            id="resume_summary"
            name="resume_summary"
            value={formData.resume_summary}
            onChange={handleChange}
            required
            rows="4"
            placeholder="Brief summary of candidate's experience and qualifications..."
          ></textarea>
        </div>

        <div className="form-group">
          <label htmlFor="preferred_interview_date">Preferred Interview Date</label>
          <input
            type="datetime-local"
            id="preferred_interview_date"
            name="preferred_interview_date"
            value={formData.preferred_interview_date}
            onChange={handleChange}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+1 (555) 123-4567"
            />
          </div>

          <div className="form-group">
            <label htmlFor="experience_years">Years of Experience</label>
            <input
              type="number"
              id="experience_years"
              name="experience_years"
              value={formData.experience_years}
              onChange={handleChange}
              min="0"
              max="50"
              step="0.5"
              placeholder="5.5"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="location">Location</label>
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleChange}
            placeholder="City, State/Country"
          />
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating Candidate...' : 'Create Candidate'}
        </button>
      </form>
    </div>
  );
};

export default CandidateForm;
