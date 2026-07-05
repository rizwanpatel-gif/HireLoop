import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { driver } from 'driver.js';
import 'driver.js/dist/driver.css';
import TourBanner from '../onboarding/TourBanner';
import { getStage, setStage, isTourDone, markTourDone } from '../onboarding/tourStorage';
import './Home.css';

const UserPlusIcon = () => (
  <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
    <circle cx="8.5" cy="7" r="4" />
    <line x1="19" y1="8" x2="19" y2="14" />
    <line x1="22" y1="11" x2="16" y2="11" />
  </svg>
);

const CalendarCheckIcon = () => (
  <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4.5" width="18" height="16" rx="3" />
    <line x1="16" y1="2.5" x2="16" y2="6.5" />
    <line x1="8" y1="2.5" x2="8" y2="6.5" />
    <line x1="3" y1="10" x2="21" y2="10" />
    <path d="M8.5 15.5l2 2 4.5-4.5" />
  </svg>
);

const Home = () => {
  const navigate = useNavigate();
  const [tourActive, setTourActive] = useState(false);

  useEffect(() => {
    // First-ever visit: nothing started yet and never completed - kick off the
    // onboarding tour by glowing the Add Candidate card.
    if (!isTourDone() && !getStage()) {
      setStage('home');
    }
    if (getStage() === 'home') {
      setTourActive(true);
      const driverObj = driver({
        showProgress: false,
        allowClose: true,
        popoverClass: 'hireloop-tour-popover',
        stagePadding: 28,
        stageRadius: 24,
      });
      driverObj.highlight({
        element: '#tour-add-candidate-card',
        popover: {
          title: 'Start here 👋',
          description: "Let's create a demo candidate together - click this card to begin.",
          side: 'bottom',
          align: 'center',
        },
      });
      return () => driverObj.destroy();
    }
  }, []);

  const handleAddCandidateClick = () => {
    if (getStage() === 'home') {
      setStage('form');
    }
    navigate('/add-candidate');
  };

  const handleSkipTour = () => {
    markTourDone();
    setTourActive(false);
  };

  return (
    <div className="tour-page-wrapper">
      {tourActive && (
        <TourBanner
          instruction="Click the 'Add Candidate' card below to begin the guided walkthrough."
          copyText={null}
          onSkip={handleSkipTour}
        />
      )}
      <div className="home">
      <div className="home-cards">
        <button id="tour-add-candidate-card" className="home-card" onClick={handleAddCandidateClick}>
          <div className="home-card-icon">
            <UserPlusIcon />
          </div>
          <h3>Add Candidate</h3>
          <p>Submit a name, email, role, and resume - the AI screens it instantly.</p>
        </button>

        <button className="home-card" onClick={() => navigate('/agent-chat')}>
          <div className="home-card-icon">
            <CalendarCheckIcon />
          </div>
          <h3>Schedule Interview</h3>
          <p>Approve, schedule, and manage candidates through a simple conversation.</p>
        </button>
      </div>
      </div>
    </div>
  );
};

export default Home;
