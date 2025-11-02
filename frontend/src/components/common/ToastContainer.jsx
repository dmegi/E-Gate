import { useEffect, useState } from "react";
import { subscribe } from "../../lib/toast";

export default function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const unsub = subscribe((t) => {
      setToasts((prev) => [...prev, t]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((x) => x.id !== t.id));
      }, 2500);
    });
    return () => unsub();
  }, []);

  return (
    <div style={{ position: "fixed", top: 16, right: 16, zIndex: 9999 }}>
      {toasts.map((t) => (
        <div
          key={t.id}
          style={{
            marginBottom: 8,
            padding: "10px 14px",
            background: t.type === "error" ? "#ef4444" : t.type === "success" ? "#22c55e" : "#334155",
            color: "#fff",
            borderRadius: 8,
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
            minWidth: 240,
          }}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}

