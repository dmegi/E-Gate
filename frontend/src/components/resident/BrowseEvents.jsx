import { useEffect, useMemo, useState } from "react";
import { api } from "../../api";
import toast from "../../lib/toast";

export default function BrowseEvents() {
  const [events, setEvents] = useState([]);
  const [my, setMy] = useState(new Set());
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);
  const [search, setSearch] = useState("");

  const loadEvents = async (p = 1) => {
    const res = await api.get(`/events/list/?page=${p}`);
    const data = res.data || {};
    setEvents(data.results || []);
    setHasNext(!!data.next);
    setHasPrev(!!data.previous);
  };

  const loadMine = async () => {
    const res = await api.get("/events/my-registrations/");
    const ids = new Set((res.data || []).map((r) => r.event));
    setMy(ids);
  };

  useEffect(() => {
    loadEvents(page).catch(() => toast.error("Failed to load events"));
  }, [page]);

  useEffect(() => {
    loadMine().catch(() => {});
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return events;
    return events.filter(
      (e) => e.title?.toLowerCase().includes(q) || e.event_type?.toLowerCase().includes(q) || e.venue?.toLowerCase().includes(q)
    );
  }, [events, search]);

  const handleRegister = async (id) => {
    try {
      await api.post(`/events/${id}/register/`);
      toast.success("Registered for event");
      await loadMine();
    } catch (e) {
      const msg = e?.response?.data?.error || e?.response?.data?.message || "Failed to register";
      toast.error(msg);
    }
  };

  const handleUnregister = async (id) => {
    try {
      await api.post(`/events/${id}/unregister/`);
      toast.success("Unregistered from event");
      await loadMine();
    } catch (e) {
      const msg = e?.response?.data?.error || e?.response?.data?.message || "Failed to unregister";
      toast.error(msg);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", textAlign: "left" }}>
      <h2>Browse Events</h2>
      <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
        <input
          placeholder="Search by title/type/venue"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: 1, padding: 8, borderRadius: 6, border: "1px solid #e5e7eb" }}
        />
        <div>
          <button disabled={!hasPrev || page === 1} onClick={() => setPage((p) => (p > 1 ? p - 1 : p))} style={{ marginRight: 6 }}>
            Prev
          </button>
          <button disabled={!hasNext} onClick={() => setPage((p) => p + 1)}>
            Next
          </button>
        </div>
      </div>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {filtered.map((e) => {
          const registered = my.has(e.id);
          return (
            <li key={e.id} style={{ background: "#fff", border: "1px solid #eee", borderRadius: 8, padding: 12, marginBottom: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{e.title}</div>
                  <div style={{ fontSize: 13, opacity: 0.8 }}>{e.event_type} • {e.venue} • {new Date(e.date).toLocaleString()}</div>
                </div>
                <div>
                  {!registered ? (
                    <button onClick={() => handleRegister(e.id)} style={{ padding: "6px 12px" }}>Register</button>
                  ) : (
                    <button onClick={() => handleUnregister(e.id)} style={{ padding: "6px 12px", background: "#ef4444", color: "#fff", border: "none", borderRadius: 4 }}>
                      Unregister
                    </button>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
      {filtered.length === 0 && <p>No events found.</p>}
    </div>
  );
}

