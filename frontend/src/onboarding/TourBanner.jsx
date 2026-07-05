import React from 'react';
import CopyButton from './CopyButton';
import './TourBanner.css';

// Bottom-fixed bar shown during onboarding: explains the current step, gives a
// copy-paste-ready command when there is one, and always offers a way out.
const TourBanner = ({ instruction, copyText, onSkip }) => (
  <div className="tour-banner">
    <div className="tour-banner-text">
      <span className="tour-banner-badge">Onboarding</span>
      {instruction}
    </div>
    <div className="tour-banner-actions">
      {copyText && (
        <div className="tour-banner-copy-row">
          <code className="tour-banner-copy-text">{copyText}</code>
          <CopyButton text={copyText} />
        </div>
      )}
      <button type="button" className="tour-banner-skip" onClick={onSkip}>
        Skip tour
      </button>
    </div>
  </div>
);

export default TourBanner;
