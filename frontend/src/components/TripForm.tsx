import { useState } from 'react';
import { Plus } from 'lucide-react';

interface Props {
  onCreate: (value: { title: string; destination: string; days: number; budget_per_person: number }) => Promise<void>;
}

export function TripForm({ onCreate }: Props) {
  const [title, setTitle] = useState('');
  const [destination, setDestination] = useState('');
  const [days, setDays] = useState(3);
  const [budget, setBudget] = useState(100);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    await onCreate({ title, destination, days, budget_per_person: budget });
    setTitle('');
    setDestination('');
  }

  return (
    <form className="stack" onSubmit={submit}>
      <label>Trip name<input required minLength={2} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Summer escape" /></label>
      <label>Destination<input required minLength={2} value={destination} onChange={(e) => setDestination(e.target.value)} placeholder="Vancouver, BC" /></label>
      <div className="two-col">
        <label>Days<input type="number" min={1} max={14} value={days} onChange={(e) => setDays(Number(e.target.value))} /></label>
        <label>Daily budget / person ($)<input type="number" min={0} value={budget} onChange={(e) => setBudget(Number(e.target.value))} /></label>
      </div>
      <button type="submit"><Plus size={16} /> Create trip</button>
    </form>
  );
}
