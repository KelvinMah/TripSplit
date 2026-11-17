import { useCallback, useEffect, useState } from 'react';
import { CalendarDays, Compass, MapPin, Sparkles, Trash2, Users, Wallet } from 'lucide-react';
import { TripForm } from './components/TripForm';
import { TravelerForm } from './components/TravelerForm';
import { api, type Conflict, type Extraction, type Trip, type Traveler } from './lib/api';

export default function App() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [conversation, setConversation] = useState('Alex: I love food and hiking, budget $60\nSam: I prefer art and coffee, avoid hiking');
  const [extraction, setExtraction] = useState<Extraction | null>(null);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [notes, setNotes] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const selected = trips.find((trip) => trip.id === selectedId);
  const refresh = useCallback(async () => {
    const data = await api.trips();
    setTrips(data);
    setSelectedId((current) => current && data.some((trip) => trip.id === current) ? current : data[0]?.id ?? null);
  }, []);

  useEffect(() => { refresh().catch((err) => setError(String(err))); }, [refresh]);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError('');
    try { await action(); } catch (err) { setError(err instanceof Error ? err.message : String(err)); }
    finally { setBusy(false); }
  }

  async function createTrip(value: { title: string; destination: string; days: number; budget_per_person: number }) {
    await run(async () => { const created = await api.createTrip(value); await refresh(); setSelectedId(created.id); setConflicts([]); setNotes([]); });
  }

  async function addTraveler(data: Omit<Traveler, 'id'>) {
    if (!selected) return;
    await run(async () => { await api.addTraveler(selected.id, data); await refresh(); });
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-icon"><Compass size={22} /></div><span>trip<span className="brand-accent">split</span></span></div>
        <p className="eyebrow">YOUR WORKSPACE</p>
        <h3>My trips <span className="count">{trips.length}</span></h3>
        <div className="trip-list">
          {trips.map((trip) => (
            <button key={trip.id} className={`trip-choice ${selectedId === trip.id ? 'active' : ''}`} onClick={() => { setSelectedId(trip.id); setConflicts([]); setNotes([]); }}>
              <MapPin size={17} /><span><strong>{trip.title}</strong><small>{trip.destination} · {trip.days} days</small></span>
            </button>
          ))}
          {trips.length === 0 && <p className="muted">No trips yet. Create your first plan.</p>}
        </div>
        <div className="sidebar-bottom"><span className="status-dot" /> Planning workspace · Local demo</div>
      </aside>

      <main className="main">
        <header className="topbar"><span>GROUP TRAVEL PLANNER</span><span className="topbar-tag"><Sparkles size={14} /> AI-assisted</span></header>
        <div className="content">
          <div className="hero"><p className="eyebrow accent">PLAN TOGETHER, TRAVEL BETTER</p><h1>Make every trip<br /><em>everyone's trip.</em></h1><p>Turn group preferences into a shared plan, surface conflicts early, and explore an itinerary that respects your budget.</p></div>
          {error && <div role="alert" className="alert error">{error}</div>}
          <div className="layout">
            <section className="panel"><div className="section-heading"><div><p className="eyebrow">GET STARTED</p><h2>Create a trip</h2></div><CalendarDays size={22} /></div><TripForm onCreate={createTrip} /></section>
            <section className="panel"><div className="section-heading"><div><p className="eyebrow">AI PREFERENCES</p><h2>Group conversation</h2></div><Sparkles size={22} /></div>
              <label>Paste your group chat<textarea rows={6} value={conversation} onChange={(e) => setConversation(e.target.value)} /></label>
              <button disabled={busy || conversation.trim().length < 5} onClick={() => run(async () => setExtraction(await api.extract(conversation)))}><Sparkles size={16} /> Extract preferences</button>
              {extraction && <div className="extraction"><p><strong>{extraction.travelers.length} travelers detected</strong> · {extraction.source}</p>
                {extraction.travelers.map((person, index) => <div className="extracted-person" key={`${person.name}-${index}`}><strong>{person.name}</strong><span>{person.interests.join(', ') || 'No interests detected'}</span>
                  {selected && <button className="tiny" disabled={busy} onClick={() => run(async () => { await api.addTraveler(selected.id, person); await refresh(); })}>Add to trip</button>}</div>)}
                <p className="muted">Review extracted details before adding. {extraction.warnings.join(' ')}</p>
              </div>}
            </section>
          </div>
          {selected && <>
            <div className="trip-header"><div><p className="eyebrow">ACTIVE TRIP</p><h2>{selected.title} <span className="destination">/ {selected.destination}</span></h2><div className="stats"><span><CalendarDays size={15} /> {selected.days} days</span><span><Wallet size={15} /> ${selected.budget_per_person}/day</span><span><Users size={15} /> {selected.travelers.length} travelers</span></div></div><button className="danger-outline" onClick={() => run(async () => { await api.deleteTrip(selected.id); await refresh(); })}><Trash2 size={15} /> Delete</button></div>
            <div className="layout"><section className="panel"><div className="section-heading"><div><p className="eyebrow">YOUR GROUP</p><h2>Travelers</h2></div><Users size={22} /></div>
              {selected.travelers.map((person) => <div className="person-row" key={person.id}><div><strong>{person.name}</strong><small>{person.interests.join(', ') || 'No interests'} {person.max_daily_budget !== null ? `· $${person.max_daily_budget}/day` : ''}</small></div><button aria-label={`Remove ${person.name}`} className="icon-button" onClick={() => run(async () => { await api.deleteTraveler(selected.id, person.id); await refresh(); })}><Trash2 size={15} /></button></div>)}
              <TravelerForm onAdd={addTraveler} /></section>
              <section className="panel"><div className="section-heading"><div><p className="eyebrow">ITINERARY ENGINE</p><h2>Generate your plan</h2></div><Compass size={22} /></div><p className="muted">Our deterministic planner scores shared interests, excludes avoided categories, and respects the strictest daily budget.</p>
                <button disabled={busy || selected.travelers.length === 0} onClick={() => run(async () => { const result = await api.generate(selected.id); setConflicts(result.conflicts); setNotes(result.notes); await refresh(); })}><Sparkles size={16} /> Generate itinerary</button>
                {conflicts.map((conflict, index) => <div className="alert warning" key={index}><strong>{conflict.type.toUpperCase()}</strong> {conflict.detail}</div>)}
                {notes.map((note) => <p className="muted" key={note}>{note}</p>)}
              </section></div>
            <section className="panel itinerary"><div className="section-heading"><div><p className="eyebrow">YOUR ADVENTURE</p><h2>Day-by-day itinerary</h2></div><MapPin size={22} /></div>
              {selected.itinerary.length === 0 ? <div className="empty">Your itinerary will appear here after you generate a plan.</div> :
                Array.from({ length: selected.days }, (_, i) => i + 1).map((day) => <div className="day" key={day}><div className="day-heading">DAY {String(day).padStart(2, '0')} <span>${selected.itinerary.filter((s) => s.day === day).reduce((sum, s) => sum + s.estimated_cost, 0)} estimated / person</span></div><div className="stops">{selected.itinerary.filter((s) => s.day === day).map((stop) => <div className="stop" key={stop.id}><span className="stop-number">{stop.position}</span><div><strong>{stop.name}</strong><p>{stop.rationale}</p><small>{stop.category} · ${stop.estimated_cost} estimated</small></div></div>)}</div></div>)}
            </section>
          </>}
          <footer>TripSplit · Portfolio demonstration · Suggested activities are not verified venues or booked reservations.</footer>
        </div>
      </main>
    </div>
  );
}
