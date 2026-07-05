// Ordered chat-stage script for the onboarding tour. Each step after the first
// is entered automatically once a new, non-error assistant reply arrives (see
// AgentChat.jsx) - the whole tour actually drives the real backend, it doesn't
// fake anything, so the copy text below has to be phrasing the app genuinely
// understands.
export const CHAT_STEPS = [
  {
    id: 'round1',
    copy: () => 'yes',
    instruction: "The AI is asking whether to send the Round 1 invite. Copy this and send it.",
  },
  {
    id: 'datetime1',
    copy: () => 'tomorrow',
    instruction: "Now it wants a date for the interview - just a day, no exact time needed. Copy this and send it.",
  },
  {
    id: 'slot1',
    copy: null,
    instruction: 'Pick any time slot below to book Round 1.',
  },
  {
    id: 'round2',
    copy: () => 'Schedule round 2 for them',
    instruction: 'Round 1 is booked! Copy this to move them to round 2.',
  },
  {
    id: 'datetime2',
    copy: () => 'next week',
    instruction: 'Give it a date for round 2.',
  },
  {
    id: 'slot2',
    copy: null,
    instruction: 'Pick a time slot for round 2.',
  },
  {
    id: 'reschedule',
    copy: () => 'Reschedule this interview',
    instruction: "Let's try rescheduling an already-booked round - copy this and send it.",
  },
  {
    id: 'datetime3',
    copy: () => 'next friday',
    instruction: 'Give it a new date for the reschedule.',
  },
  {
    id: 'slot3',
    copy: null,
    instruction: 'Pick the new time slot.',
  },
  {
    id: 'stats',
    copy: () => 'How many candidates are in the system?',
    instruction: "Rescheduled! It can also just answer questions - try this one.",
  },
  {
    id: 'lookup',
    copy: (name) => `Which round is ${name} on?`,
    instruction: 'Ask it about this specific candidate.',
  },
  {
    id: 'reject',
    copy: () => 'Reject them',
    instruction: "Last step - let's see the rejection flow too.",
  },
];

export const DEMO_RESUME_TEXT = `Full-Stack Software Engineer with 5+ years of experience building and scaling production web applications. Proficient in Python (Django, FastAPI, Flask), JavaScript/TypeScript, React, Node.js, and SQL/PostgreSQL. Experienced with REST API design, microservices architecture, Docker, CI/CD pipelines, and cloud deployment on AWS/GCP. Led a team of 4 engineers redesigning a legacy monolith into microservices, improving system throughput by 40%. Strong background in agile development, code review, mentoring, and writing well-tested code (pytest, Jest). B.S. in Computer Science.`;
