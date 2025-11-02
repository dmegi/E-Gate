import { useEffect, useState } from "react";
import { api } from "../../api";

export default function MyRegistrations() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await api.get("/events/my-registrations/");
        if (!mounted) return;
        setItems(res.data || []);
      } catch (e) {
        setError("Failed to load registrations");
      } finally {
        setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  if (loading) return <p>Loading my registrations...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", textAlign: "left" }}>
      <h2>My Event Registrations</h2>
      {items.length === 0 ? (
        <p>No registrations yet.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {items.map((r) => (
            <li key={r.id} style={{ background: "#fff", border: "1px solid #eee", borderRadius: 8, padding: 12, marginBottom: 8 }}>
              <div style={{ fontWeight: 600 }}>{r.event_title || r.event}</div>
              <div style={{ opacity: 0.8, fontSize: 14 }}>Registered at: {new Date(r.registered_at).toLocaleString()}</div>
              <div style={{ fontSize: 14 }}>Attendance confirmed: {r.attendance_confirmed ? "Yes" : "No"}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

