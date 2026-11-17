import { useState } from 'react';
import type { Traveler } from '../lib/api';

interface Props {
  onAdd: (data: Omit<Traveler, 'id'>) => Promise<void>;
}

const split = (value: string) => value.split(',').map((part) => part.trim().toLowerCase()).filter(Boolean);

export function TravelerForm({ onAdd }: Props) {
  const [name, setName] = useState('');
  const [interests, setInterests] = useState('');
  const [avoid, setAvoid] = useState('');
  const [budget, setBudget] = useState('');

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    await onAdd({ name, interests: split(interests), avoid: split(avoid), max_daily_budget: budget ? Number(budget) : null, notes: '' });
    setName('');
    setInterests('');
    setAvoid('');
    setBudget('');
  }

  return (
    <form className="stack" onSubmit={submit}>
      <label>Name<input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Alex" /></label>
      <label>Interests (comma-separated)<input value={interests} onChange={(e) => setInterests(e.target.value)} placeholder="food, hiking, art" /></label>
      <label>Avoid (comma-separated)<input value={avoid} onChange={(e) => setAvoid(e.target.value)} placeholder="nightlife" /></label>
      <label>Max daily budget ($)<input type="number" min={0} value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="Optional" /></label>
      <button type="submit" className="secondary">Add traveler</button>
    </form>
  );
}
