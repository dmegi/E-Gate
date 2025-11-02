import { useState, useEffect } from "react";
import AdminLogin from "./components/AdminLogin";
import ResidentLogin from "./components/ResidentLogin";
import MyRegistrations from "./components/resident/MyRegistrations";
import BrowseEvents from "./components/resident/BrowseEvents";
import ProfileCard from "./components/resident/ProfileCard";
import ToastContainer from "./components/common/ToastContainer";
import EventSelector from "./components/EventSelector";
import QrScanner from "./components/QrScanner";
import DashboardHome from "./components/dashboard/DashboardHome";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [viewMode, setViewMode] = useState("scanner"); // "scanner" or "dashboard"
  const [loginType, setLoginType] = useState("admin"); // 'admin' | 'resident'
  const [role, setRole] = useState("");

  // Check token on load
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const r = localStorage.getItem("role") || "";
    if (token) setIsLoggedIn(true);
    if (r) setRole(r);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    setIsLoggedIn(false);
    setSelectedEvent(null);
    setRole("");
  };

  return (
    <div className="app-wrapper">
      <ToastContainer />
      <h1>Barangay E-Gate QR Attendance System</h1>

      {/* Not logged in: choose role and log in */}
      {!isLoggedIn ? (
        <>
          <div style={{ marginBottom: 12 }}>
            <button onClick={() => setLoginType("admin")} style={{ marginRight: 8, padding: "6px 12px", background: loginType === "admin" ? "#4caf50" : "#e0e0e0", color: loginType === "admin" ? "#fff" : "#000", border: "none", borderRadius: 4 }}>Admin</button>
            <button onClick={() => setLoginType("resident")} style={{ padding: "6px 12px", background: loginType === "resident" ? "#4caf50" : "#e0e0e0", color: loginType === "resident" ? "#fff" : "#000", border: "none", borderRadius: 4 }}>Resident</button>
          </div>
          {loginType === "admin" ? (
            <AdminLogin onLogin={() => { setIsLoggedIn(true); setRole(localStorage.getItem("role") || "Administrator"); }} />
          ) : (
            <ResidentLogin onLogin={() => { setIsLoggedIn(true); setRole(localStorage.getItem("role") || "Resident"); }} />
          )}
        </>
      ) : (
        <>
          {role === "Administrator" ? (
            <>
              {/* Admin navigation */}
              <div style={{ marginBottom: "20px" }}>
                <button
                  onClick={() => setViewMode("scanner")}
                  style={{
                    margin: "5px",
                    padding: "8px 16px",
                    background:
                      viewMode === "scanner" ? "#4caf50" : "#e0e0e0",
                    color: viewMode === "scanner" ? "white" : "black",
                    border: "none",
                    borderRadius: "4px",
                  }}
                >
                  Scanner Mode
                </button>

                <button
                  onClick={() => setViewMode("dashboard")}
                  style={{
                    margin: "5px",
                    padding: "8px 16px",
                    background:
                      viewMode === "dashboard" ? "#4caf50" : "#e0e0e0",
                    color: viewMode === "dashboard" ? "white" : "black",
                    border: "none",
                    borderRadius: "4px",
                  }}
                >
                  Dashboard
                </button>

                <button
                  onClick={handleLogout}
                  style={{
                    margin: "5px",
                    padding: "8px 16px",
                    background: "#f44336",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                  }}
                >
                  Logout
                </button>
              </div>

              {/* Admin view modes */}
              {viewMode === "scanner" ? (
                <>
                  <EventSelector onSelect={(id) => setSelectedEvent(id)} />
                  {selectedEvent ? (
                    <QrScanner eventId={selectedEvent} />
                  ) : (
                    <p>Please select an event to start scanning.</p>
                  )}
                </>
              ) : (
                <DashboardHome />
              )}
            </>
          ) : (
            <>
              <div style={{ marginBottom: 12 }}>
                <button onClick={handleLogout} style={{ padding: "8px 16px", background: "#f44336", color: "white", border: "none", borderRadius: 4, marginRight: 8 }}>Logout</button>
                <button onClick={() => setViewMode("browse") } style={{ padding: "8px 16px", marginRight: 8, background: viewMode === 'browse' ? '#4caf50' : '#e0e0e0', color: viewMode === 'browse' ? '#fff' : '#000', border: 'none', borderRadius: 4 }}>Browse</button>
                <button onClick={() => setViewMode("mine") } style={{ padding: "8px 16px", marginRight: 8, background: viewMode === 'mine' ? '#4caf50' : '#e0e0e0', color: viewMode === 'mine' ? '#fff' : '#000', border: 'none', borderRadius: 4 }}>My Registrations</button>
                <button onClick={() => setViewMode("profile") } style={{ padding: "8px 16px", background: viewMode === 'profile' ? '#4caf50' : '#e0e0e0', color: viewMode === 'profile' ? '#fff' : '#000', border: 'none', borderRadius: 4 }}>Profile</button>
              </div>
              {viewMode === 'browse' && <BrowseEvents />}
              {viewMode === 'mine' && <MyRegistrations />}
              {viewMode === 'profile' && <ProfileCard />}
            </>
          )}
        </>
      )}
    </div>
  );
}

export default App;
