import { useState } from "react";
import EventList from "./EventList";
import EventDetails from "./EventDetails";
import AttendanceTable from "./AttendanceTable";
import RegistrantsList from "./RegistrantsList";
import CreateEventForm from "./CreateEventForm";

export default function DashboardHome() {
  const [selectedEvent, setSelectedEvent] = useState(null);

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <h2>Admin Dashboard</h2>
        <EventList onSelectEvent={setSelectedEvent} activeId={selectedEvent} />
      </div>

      <div className="content">
        <div className="content-inner">
          {selectedEvent ? (
            <>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <h1 style={{ margin: 0 }}>Event Details</h1>
                <button onClick={() => setSelectedEvent(null)} style={{ padding: "6px 12px" }}>Back to Events</button>
              </div>
              <EventDetails eventId={selectedEvent} />
              <RegistrantsList eventId={selectedEvent} />
              <AttendanceTable eventId={selectedEvent} />
            </>
          ) : (
            <>
              <CreateEventForm onCreated={() => { /* could refresh list via key, kept simple */ }} />
              <p>Select an event to view details and attendance.</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
