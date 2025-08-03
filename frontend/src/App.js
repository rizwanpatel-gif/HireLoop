import React from 'react';
import CandidateForm from './components/CandidateForm';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <h1>RHero - Interview Management System</h1>
        <p>Streamline your hiring process with AI-powered candidate management</p>
      </header>
      
      <main className="app-main">
        <CandidateForm />
      </main>
      
      <footer className="app-footer">
        <p>&copy; 2024 RHero. Simplifying recruitment, one candidate at a time.</p>
      </footer>
    </div>
  );
}

export default App;
