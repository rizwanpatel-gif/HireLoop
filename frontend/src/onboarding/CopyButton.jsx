import React, { useState } from 'react';
import './CopyButton.css';

const CopyButton = ({ text, label = 'Copy' }) => {
  const [copied, setCopied] = useState(false);

  const handleClick = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (err) {
      console.error('Clipboard copy failed:', err);
    }
  };

  return (
    <button type="button" className="tour-copy-btn" onClick={handleClick}>
      {copied ? 'Copied ✓' : label}
    </button>
  );
};

export default CopyButton;
