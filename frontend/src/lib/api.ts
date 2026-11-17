export interface Traveler {
  id: string;
  name: string;
  interests: string[];
  avoid: string[];
  max_daily_budget: number | null;
  notes: string;
}

export interface Stop {
  id: string;
  day: number;
  position: number;
  name: string;
  category: string;
  estimated_cost: number;
  rationale: string;
  place_id: string | null;
}

export interface Trip {
  id: string;
  title: string;
  destination: string;
  days: number;
  budget_per_person: number;
  created_at: string;
  travelers: Traveler[];
  itinerary: Stop[];
}

export interface Conflict {
  type: string;
  travelers: string[];
  detail: string;
}

export interface Generation {
  itinerary: Stop[];
  conflicts: Conflict[];
  notes: string[];
}

export interface Extraction {
  travelers: Omit<Traveler, 'id'>[];
  destinations: string[];
  shared_interests: string[];
  warnings: string[];
  source: string;
}

const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}/api${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export const api = {
  trips: () => request<Trip[]>('/trips'),
  createTrip: (data: { title: string; destination: string; days: number; budget_per_person: number }) =>
    request<Trip>('/trips', { method: 'POST', body: JSON.stringify(data) }),
  deleteTrip: (id: string) => request<void>(`/trips/${id}`, { method: 'DELETE' }),
  addTraveler: (id: string, data: Omit<Traveler, 'id'>) =>
    request<Traveler>(`/trips/${id}/travelers`, { method: 'POST', body: JSON.stringify(data) }),
  deleteTraveler: (id: string, travelerId: string) =>
    request<void>(`/trips/${id}/travelers/${travelerId}`, { method: 'DELETE' }),
  extract: (conversation: string) =>
    request<Extraction>('/preferences/extract', { method: 'POST', body: JSON.stringify({ conversation }) }),
  generate: (id: string) => request<Generation>(`/trips/${id}/generate`, { method: 'POST' }),
};
