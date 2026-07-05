import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './components/Home';
import CandidateForm from './components/CandidateForm';
import AgentChat from './components/AgentChat';
import './onboarding/tourPopover.css';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <Link to="/" className="app-brand">HireLoop</Link>
          <p>AI-screened candidates, hired through a conversation.</p>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/add-candidate" element={<CandidateForm />} />
            <Route path="/agent-chat" element={<AgentChat />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
