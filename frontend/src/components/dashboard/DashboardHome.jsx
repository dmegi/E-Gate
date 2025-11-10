import { useState } from "react";
import EventList from "./EventList";
import EventDetails from "./EventDetails";
import AttendanceTable from "./AttendanceTable";
import RegistrantsList from "./RegistrantsList";
import CreateEventForm from "./CreateEventForm";
import styles from "./DashboardHome.module.css";
import ui from "./DashboardUI.module.css";
import ErrorBoundary from "./ErrorBoundary";

export default function DashboardHome() {
  const [selectedEvent, setSelectedEvent] = useState(null);

  return (
    <div className={`dashboard-container ${styles.container}`}>
      <div className={`sidebar ${styles.sidebar}`}>
        <h2>Admin Dashboard</h2>
        <EventList onSelectEvent={setSelectedEvent} activeId={selectedEvent} />
      </div>

      <div className={`content ${styles.content}`}>
        <div className={`content-inner ${styles.contentInner}`}>
          {selectedEvent ? (
            <>
              <div className={styles.headerRow}>
                <h1 style={{ margin: 0 }}>Event Details</h1>
                <button className={`${ui.button} ${styles.backButton}`} onClick={() => setSelectedEvent(null)}>Back to Events</button>
              </div>
              <ErrorBoundary label="EventDetails">
                <EventDetails eventId={selectedEvent} />
              </ErrorBoundary>
              <ErrorBoundary label="RegistrantsList">
                <RegistrantsList eventId={selectedEvent} />
              </ErrorBoundary>
              <ErrorBoundary label="AttendanceTable">
                <AttendanceTable eventId={selectedEvent} />
              </ErrorBoundary>
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
