import { useEffect, useRef, useState } from "react";
import { Html5QrcodeScanner } from "html5-qrcode";
import { api, getAuthHeaders } from "../api";

export default function QRScanner({ eventId }) {
  const [message, setMessage] = useState("");
  const scannerRef = useRef(null);

  useEffect(() => {
    const scanner = new Html5QrcodeScanner("reader", {
      fps: 10,
      qrbox: { width: 250, height: 250 },
    });

    scanner.render(onScanSuccess, onScanError);

    function onScanSuccess(decodedText) {
      scanner.clear();
      markAttendance(decodedText);
    }

    function onScanError(err) {
      // ignore scan errors
    }

    async function markAttendance(decodedText) {
      const barangayId = decodedText.split("Barangay ID: ")[1]?.split("\n")[0];
      if (!barangayId) return setMessage("Invalid QR format");

      try {
        const res = await api.post(
          "/events/attendance/mark/",
          { barangay_id: barangayId, event_id: eventId },
          { headers: getAuthHeaders() }
        );

        setMessage(res.data.message || "Attendance marked successfully!");
      } catch (err) {
        setMessage(err.response?.data?.error || "Failed to mark attendance");
      }
    }

    scannerRef.current = scanner;
    return () => scanner.clear();
  }, []);

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>Barangay E-Gate QR Scanner</h2>
      <div id="reader" style={{ width: "300px", margin: "auto" }}></div>
      <p><b>Status:</b> {message}</p>
    </div>
  );
}
