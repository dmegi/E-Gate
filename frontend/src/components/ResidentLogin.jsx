import { useState } from "react";
import { api } from "../api";

export default function ResidentLogin({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const res = await api.post("/accounts/login/resident/", { username, password });
      const access = res?.data?.tokens?.access;
      const refresh = res?.data?.tokens?.refresh;
      if (access) localStorage.setItem("access_token", access);
      if (refresh) localStorage.setItem("refresh_token", refresh);
      const role = res?.data?.meta?.role || "Resident";
      localStorage.setItem("role", role);
      setMessage(res?.data?.message || "Login successful!");
      onLogin?.();
    } catch (err) {
      setMessage(err.response?.data?.error || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", marginTop: 20 }}>
      <div className="card" style={{ width: 360 }}>
        <h2 style={{ marginTop: 0 }}>Resident Login</h2>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ width: "100%", margin: "6px 0", padding: "10px", borderRadius: 6, border: "1px solid #e5e7eb" }}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: "100%", margin: "6px 0", padding: "10px", borderRadius: 6, border: "1px solid #e5e7eb" }}
            required
          />
          <button type="submit" disabled={loading} style={{ width: "100%", padding: "10px 14px", marginTop: 8 }}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p>{message}</p>
      </div>
    </div>
  );
}
