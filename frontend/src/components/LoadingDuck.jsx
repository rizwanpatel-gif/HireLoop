import React from 'react';
import './LoadingDuck.css';

// A little white duck "running" toward the viewer (bounce + scale-up pulse +
// kicking legs) while the resume gets AI-screened - shown as a dedicated
// overlay card instead of just disabling the submit button.
const LoadingDuck = ({ message = 'Screening the resume...' }) => (
  <div className="loading-duck-overlay">
    <div className="loading-duck-card">
      <svg className="loading-duck-svg" viewBox="0 0 120 130" xmlns="http://www.w3.org/2000/svg">
        <ellipse className="duck-shadow" cx="60" cy="118" rx="26" ry="6" fill="#e4d9fc" />
        <g className="duck-body-group">
          <ellipse className="duck-leg duck-leg-left" cx="48" cy="102" rx="6" ry="9" fill="#f5a623" />
          <ellipse className="duck-leg duck-leg-right" cx="72" cy="102" rx="6" ry="9" fill="#f5a623" />
          <ellipse cx="60" cy="76" rx="34" ry="28" fill="#ffffff" stroke="#e6e6ee" strokeWidth="1.5" />
          <ellipse cx="32" cy="80" rx="10" ry="16" fill="#f2f0fb" />
          <ellipse cx="88" cy="80" rx="10" ry="16" fill="#f2f0fb" />
          <circle cx="60" cy="40" r="24" fill="#ffffff" stroke="#e6e6ee" strokeWidth="1.5" />
          <path d="M45 46 Q60 60 75 46 Q60 53 45 46 Z" fill="#f5a623" />
          <circle cx="50" cy="36" r="3.2" fill="#2b2b33" />
          <circle cx="70" cy="36" r="3.2" fill="#2b2b33" />
          <circle cx="41" cy="45" r="4" fill="#ffd9e6" opacity="0.7" />
          <circle cx="79" cy="45" r="4" fill="#ffd9e6" opacity="0.7" />
        </g>
      </svg>
      <p className="loading-duck-text">{message}</p>
      <div className="loading-duck-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
  </div>
);

export default LoadingDuck;
