import React, { useState, useEffect, useRef } from 'react';
import { driver } from 'driver.js';
import 'driver.js/dist/driver.css';
import TourBanner from '../onboarding/TourBanner';
import { CHAT_STEPS } from '../onboarding/tourSteps';
import { getStage, setStage, getTourCandidateName, markTourDone } from '../onboarding/tourStorage';
import { API_BASE_URL } from '../config';
import './AgentChat.css';

const ISO_DATETIME_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)?$/;

// A clicked slot button sends its exact ISO datetime as the message (so the
// backend can parse it precisely) - that's correct to store, but showing the
// raw ISO string back to HR isn't the friendly label they clicked. Reformat
// just for display when a message turns out to be one of these.
const formatMessageContent = (content) => {
  if (typeof content === 'string' && ISO_DATETIME_RE.test(content.trim())) {
    const date = new Date(content);
    if (!isNaN(date)) {
      return date.toLocaleString('en-US', {
        weekday: 'short', month: 'short', day: 'numeric',
        hour: 'numeric', minute: '2-digit', hour12: true,
      });
    }
  }
  return content;
};

const AgentChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  const [tourStepIndex, setTourStepIndex] = useState(() => {
    const stage = getStage();
    if (stage && stage.startsWith('chat:')) {
      const idx = CHAT_STEPS.findIndex(s => s.id === stage.slice(5));
      return idx >= 0 ? idx : null;
    }
    return null;
  });
  const [tourJustCompleted, setTourJustCompleted] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const lastSeenAssistantIdRef = useRef(null);
  const tourSeededRef = useRef(false);

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  // Advance the onboarding tour reactively off real assistant replies - this
  // genuinely drives the backend, so we detect progress the same way a human
  // would: a new, non-error assistant message means the last step worked.
  useEffect(() => {
    if (tourStepIndex === null || messages.length === 0) return;
    const lastMsg = messages[messages.length - 1];
    if (lastMsg.role !== 'assistant') return;

    if (!tourSeededRef.current) {
      // The message already in history when we entered this stage is what
      // prompted it - don't treat it as "new progress" to advance past.
      lastSeenAssistantIdRef.current = lastMsg.id;
      tourSeededRef.current = true;
      return;
    }
    if (lastMsg.id === lastSeenAssistantIdRef.current) return;
    lastSeenAssistantIdRef.current = lastMsg.id;

    if (/sorry/i.test(lastMsg.content || '')) return; // let them retry the same step

    const next = tourStepIndex + 1;
    if (next >= CHAT_STEPS.length) {
      markTourDone();
      setTourStepIndex(null);
      setTourJustCompleted(true);
      setTimeout(() => setTourJustCompleted(false), 5000);
    } else {
      setStage(`chat:${CHAT_STEPS[next].id}`);
      setTourStepIndex(next);
    }
  }, [messages, tourStepIndex]);

  // Point Driver.js's glow/arrow at whatever the current tour step is about.
  useEffect(() => {
    if (tourStepIndex === null) return;
    const step = CHAT_STEPS[tourStepIndex];
    const driverObj = driver({ showProgress: false, allowClose: true, popoverClass: 'hireloop-tour-popover' });

    if (step.id.startsWith('slot')) {
      const timer = setTimeout(() => {
        const all = document.querySelectorAll('.agent-chat-slots');
        const el = all[all.length - 1];
        if (el) {
          driverObj.highlight({ element: el, popover: { description: step.instruction, side: 'top', align: 'center' } });
        }
      }, 150);
      return () => { clearTimeout(timer); driverObj.destroy(); };
    }

    driverObj.highlight({
      element: '#agent-chat-input-field',
      popover: { description: step.instruction, side: 'top', align: 'center' },
    });
    return () => driverObj.destroy();
  }, [tourStepIndex]);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agent-chat/history`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (err) {
      console.error('Error fetching chat history:', err);
    } finally {
      setInitialLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/agent-chat/history`, { method: 'DELETE' });
      setMessages([]);
      setError(null);
    } catch (err) {
      setError('Network error. Please check if the backend server is running.');
    }
  };

  // actualMessage is what's sent to the backend (e.g. a slot's exact ISO
  // datetime); displayText is what shows in the optimistic HR bubble (e.g. a
  // friendly "10:30 AM" instead of the raw ISO string).
  const sendMessage = async (actualMessage, displayText) => {
    if (!actualMessage || sending) return;
    setSending(true);
    setError(null);

    setMessages(prev => [...prev, { id: `local-${Date.now()}`, role: 'hr', content: displayText ?? actualMessage }]);

    try {
      const response = await fetch(`${API_BASE_URL}/api/agent-chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: actualMessage }),
      });

      if (response.ok) {
        await fetchHistory();
      } else {
        const errBody = await response.json();
        setError(errBody.detail || 'Failed to send message');
      }
    } catch (err) {
      setError('Network error. Please check if the backend server is running.');
    } finally {
      setSending(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const text = input.trim();
    setInput('');
    await sendMessage(text);
  };

  const handleSlotClick = async (slot) => {
    await sendMessage(slot.iso, slot.label);
  };

  return (
    <div className="tour-page-wrapper">
      {tourStepIndex !== null && (
        <TourBanner
          instruction={CHAT_STEPS[tourStepIndex].instruction}
          copyText={CHAT_STEPS[tourStepIndex].copy ? CHAT_STEPS[tourStepIndex].copy(getTourCandidateName()) : null}
          onSkip={() => { markTourDone(); setTourStepIndex(null); }}
        />
      )}
      {tourJustCompleted && (
        <TourBanner
          instruction="🎉 Tour complete! You've now seen the full hiring flow - confirm, schedule, reschedule, ask questions, and reject."
          copyText={null}
          onSkip={() => setTourJustCompleted(false)}
        />
      )}
      <div className="agent-chat">
      <div className="agent-chat-header">
        <div className="agent-chat-header-row">
          <div>
            <h2>Schedule Interview</h2>
            <p>Approve round-1 invites, schedule interviews, and manage candidates in plain English.</p>
          </div>
          <button type="button" className="agent-chat-new-btn" onClick={handleNewChat}>
            New Chat
          </button>
        </div>
      </div>

      <div className="agent-chat-messages">
        {initialLoading && (
          <div className="agent-chat-empty">Loading chat...</div>
        )}
        {!initialLoading && messages.length === 0 && (
          <div className="agent-chat-empty">No messages yet. Add a candidate to get started.</div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`agent-chat-message ${m.role}`}>
            <div className="agent-chat-bubble">
              {formatMessageContent(m.content)}
              {m.role === 'assistant' && m.metadata?.type === 'slot_options' && (
                <div className="agent-chat-slots">
                  {m.metadata.slots.map((slot) => (
                    <button
                      key={slot.iso}
                      type="button"
                      className="agent-chat-slot-btn"
                      disabled={sending}
                      onClick={() => handleSlotClick(slot)}
                    >
                      {slot.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {sending && (
          <div className="agent-chat-message assistant">
            <div className="agent-chat-bubble agent-chat-typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <div className="agent-chat-error">{error}</div>}

      <form className="agent-chat-input-row" onSubmit={handleSend}>
        <input
          id="agent-chat-input-field"
          type="text"
          placeholder="Type your reply (e.g. 'yes', or 'July 12 2026 at 3pm')..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={sending}
        />
        <button type="submit" disabled={sending || !input.trim()}>
          {sending ? 'Sending' : 'Send'}
        </button>
      </form>

      </div>
    </div>
  );
};

export default AgentChat;
