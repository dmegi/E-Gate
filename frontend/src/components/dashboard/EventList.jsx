import { useEffect, useMemo, useState } from "react";
import { api } from "../../api";

export default function EventList({ onSelectEvent, activeId }) {
  const [events, setEvents] = useState([]);

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("date_desc");
  const [page, setPage] = useState(1);
  const pageSize = 20; const [hasNext, setHasNext] = useState(false); const [hasPrev, setHasPrev] = useState(false);

  useEffect(() => {
    const orderingParam =
      sortBy === "date_asc" ? "date" :
      sortBy === "title_asc" ? "title" :
      sortBy === "title_desc" ? "-title" : "-date";
    const q = encodeURIComponent(search.trim());
    api
      .get(`/events/list/?page=${page}&ordering=${orderingParam}${q ? `&q=${q}` : ""}`)
      .then((res) => {
        const data = res.data || {};
        setEvents(data.results || []);
        setHasNext(!!data.next);
        setHasPrev(!!data.previous);
      })
      .catch((err) => console.error(err));
  }, [page, search, sortBy]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    let list = !q
      ? [...events]
      : events.filter(
          (e) =>
            e.title?.toLowerCase().includes(q) ||
            e.event_type?.toLowerCase().includes(q) ||
            e.venue?.toLowerCase().includes(q)
        );

    switch (sortBy) {
      case "date_asc":
        list.sort((a, b) => new Date(a.date) - new Date(b.date));
        break;
      case "title_asc":
        list.sort((a, b) => (a.title || "").localeCompare(b.title || ""));
        break;
      case "title_desc":
        list.sort((a, b) => (b.title || "").localeCompare(a.title || ""));
        break;
      case "date_desc":
      default:
        list.sort((a, b) => new Date(b.date) - new Date(a.date));
    }

    return list;
  }, [events, search, sortBy]);

  const currentPage = page;
  const paged = filtered; // already server-paginated

  const goPrev = () => setPage((p) => (p > 1 && hasPrev ? p - 1 : p));
  const goNext = () => hasNext && setPage((p) => p + 1);

  return (
    <div>
      <h3>Events</h3>
      <div style={{ marginBottom: 10 }}>
        <input
          placeholder="Search by title/type/venue"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          style={{ width: "100%", padding: 8, borderRadius: 6, border: "1px solid #e5e7eb" }}
        />
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} style={{ padding: 6, borderRadius: 6 }}>
            <option value="date_desc">Date: Newest first</option>
            <option value="date_asc">Date: Oldest first</option>
            <option value="title_asc">Title: A to Z</option>
            <option value="title_desc">Title: Z to A</option>
          </select>
          <div>
            <button onClick={goPrev} disabled={!hasPrev || currentPage === 1} style={{ marginRight: 6 }}>Prev</button>
            <span>Page {currentPage}</span>
            <button onClick={goNext} disabled={!hasNext} style={{ marginLeft: 6 }}>Next</button>
          </div>
        </div>
      </div>
      <ul className="event-list">
        {paged.map((event) => {
          const isActive = activeId === event.id;
          return (
            <li
              key={event.id}
              onClick={() => onSelectEvent(event.id)}
              style={{
                cursor: "pointer",
                background: isActive ? "#22c55e" : "#f3f4f6",
                color: isActive ? "white" : "inherit",
                margin: "5px",
                padding: "10px",
                borderRadius: "6px",
              }}
            >
              {event.title} - {event.event_type}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

















