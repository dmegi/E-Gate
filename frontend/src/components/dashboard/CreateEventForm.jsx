import { useState } from "react";
import { api } from "../../api";
import toast from "../../lib/toast";

const DEFAULTS = {
  title: "",
  event_type: "community",
  date: "",
  venue: "",
  capacity: "",
  registration_open: "",
  registration_close: "",
};

export default function CreateEventForm({ onCreated }) {
  const [form, setForm] = useState(DEFAULTS);
  const [busy, setBusy] = useState(false);

  const update = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const payload = {
        title: form.title,
        event_type: form.event_type,
        date: form.date,
        venue: form.venue,
        capacity: form.capacity ? Number(form.capacity) : null,
        registration_open: form.registration_open || null,
        registration_close: form.registration_close || null,
      };
      const res = await api.post("/events/create/", payload);
      toast.success("Event created");
      setForm(DEFAULTS);
      onCreated?.(res.data);
    } catch (e) {
      const msg = e?.response?.data?.error || JSON.stringify(e?.response?.data) || "Failed to create event";
      toast.error(msg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <h3 style={{ marginTop: 0 }}>Create Event</h3>
      <form onSubmit={submit} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        <input name="title" placeholder="Title" value={form.title} onChange={update} required />
        <select name="event_type" value={form.event_type} onChange={update}>
          <option value="medical">medical</option>
          <option value="vaccination">vaccination</option>
          <option value="assembly">assembly</option>
          <option value="relief">relief</option>
          <option value="community">community</option>
          <option value="sk_election">sk election</option>
        </select>
        <input name="date" type="datetime-local" value={form.date} onChange={update} required />
        <input name="venue" placeholder="Venue" value={form.venue} onChange={update} />
        <input name="capacity" type="number" min="0" placeholder="Capacity (optional)" value={form.capacity} onChange={update} />
        <input name="registration_open" type="datetime-local" placeholder="Open (optional)" value={form.registration_open} onChange={update} />
        <input name="registration_close" type="datetime-local" placeholder="Close (optional)" value={form.registration_close} onChange={update} />
        <div style={{ gridColumn: "1 / -1", textAlign: "right" }}>
          <button type="submit" disabled={busy} style={{ padding: "8px 16px" }}>{busy ? "Creating..." : "Create"}</button>
        </div>
      </form>
    </div>
  );
}

