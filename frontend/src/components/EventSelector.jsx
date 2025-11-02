import { useEffect, useState } from "react";
import { api } from "../api";

export default function EventSelector({ onSelect }) {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function fetchEvents() {
      try {
        const res = await api.get("/events/");
        setEvents(res.data);
      } catch (err) {
        setMessage("Failed to load events");
      }
    }
    fetchEvents();
  }, []);

  const handleSelect = (e) => {
    const eventId = Number(e.target.value);
    setSelectedEvent(eventId);
    onSelect(eventId);
  };

  return (
    <div style={{ margin: "20px auto", textAlign: "center" }}>
      <h3>Select Event</h3>
      <select value={selectedEvent} onChange={handleSelect}>
        <option value="">-- Select an Event --</option>
        {events.map((event) => (
          <option key={event.id} value={event.id}>
            {event.title} ({event.event_type})
          </option>
        ))}
      </select>
      <p>{message}</p>
    </div>
  );
}
