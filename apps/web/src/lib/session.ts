export const generateSessionId = (): string => {
  return crypto.randomUUID();
};

export const setSessionId = (sessionId: string): void => {
  if (typeof window === 'undefined') {
    return;
  }
  sessionStorage.setItem('optima-session-id', sessionId);
};

export const createNewSessionId = (): string => {
  const sessionId = generateSessionId();
  setSessionId(sessionId);
  return sessionId;
};
