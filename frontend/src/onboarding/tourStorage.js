// Tour state only needs to survive page navigation (Home -> CandidateForm ->
// AgentChat), not live-sync across simultaneously mounted components, so plain
// localStorage read/writes are enough - no React Context needed.
const STAGE_KEY = 'hireloop_tour_stage';
const DONE_KEY = 'hireloop_tour_completed';
const NAME_KEY = 'hireloop_tour_candidate_name';

export const getStage = () => localStorage.getItem(STAGE_KEY);
export const setStage = (stage) => localStorage.setItem(STAGE_KEY, stage);
export const clearStage = () => localStorage.removeItem(STAGE_KEY);

export const isTourDone = () => localStorage.getItem(DONE_KEY) === 'true';
export const markTourDone = () => {
  localStorage.setItem(DONE_KEY, 'true');
  localStorage.removeItem(STAGE_KEY);
};

export const getTourCandidateName = () => localStorage.getItem(NAME_KEY) || 'them';
export const setTourCandidateName = (name) => localStorage.setItem(NAME_KEY, name);
