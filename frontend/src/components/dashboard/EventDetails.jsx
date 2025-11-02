import { useEffect, useState } from "react";
import { api } from "../../api";

export default function EventDetails({ eventId }) {
  const [event, setEvent] = useState(null);

  useEffect(() => {
    api
      .get(`/events/${eventId}/`)
      .then((res) => setEvent(res.data))
      .catch((err) => console.error(err));
  }, [eventId]);

  if (!event) return <p>Loading event details...</p>;

  return (
    <div className="card">
      <h2>{event.title}</h2>
      <p><b>Type:</b> {event.event_type}</p>
      <p><b>Venue:</b> {event.venue}</p>
      <p><b>Status:</b> {event.status}</p>
      <p><b>Date:</b> {new Date(event.date).toLocaleString()}</p>
      <p><b>Description:</b> {event.description}</p>
    </div>
  );
}
