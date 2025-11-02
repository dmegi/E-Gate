import { useEffect, useState } from "react";
import { api } from "../../api";

export default function RegistrantsList({ eventId }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!eventId) return;
    setLoading(true);
    setError("");
    api
      .get(`/events/${eventId}/registrants/`)
      .then((res) => setRows(res.data || []))
      .catch(() => setError("Failed to load registrants"))
      .finally(() => setLoading(false));
  }, [eventId]);

  if (!eventId) return null;
  if (loading) return <div className="card">Loading registrants...</div>;
  if (error) return <div className="card">{error}</div>;

  return (
    <div className="card">
      <h3>Registrants</h3>
      {rows.length === 0 ? (
        <p>No registrants yet.</p>
      ) : (
        <div className="table-container">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Resident</th>
                <th>Registered At</th>
                <th>Checked In?</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{r.resident_username}</td>
                  <td>{new Date(r.registered_at).toLocaleString()}</td>
                  <td>{r.attendance_confirmed ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

