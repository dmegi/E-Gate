import { useEffect, useState } from "react";
import { api } from "../../api";

export default function ProfileCard() {
  const [profile, setProfile] = useState(null);
  const [idInfo, setIdInfo] = useState(null);
  const [error, setError] = useState("");
  const [qrDataUrl, setQrDataUrl] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [p, v] = await Promise.all([
          api.get("/residents/profile/"),
          api.get("/residents/virtual-id/"),
        ]);
        setProfile(p.data);
        setIdInfo(v.data);
      } catch (e) {
        setError("Failed to load profile");
      }
    })();
  }, []);

  const payload = `Barangay ID: ${profile?.barangay_id || ""}\nName: ${profile?.user?.username || ""}`;

  useEffect(() => {
    let active = true;
    async function gen() {
      try {
        // Try normal dynamic import; if not installed, this will fail and we fall back.
        let QRModule;
        try {
          QRModule = await import("qrcode");
        } catch (e) {
          // Prevent Vite from trying to prebundle; still requires package for actual QR rendering.
          QRModule = await import(/* @vite-ignore */ "qrcode");
        }
        const QRCode = QRModule.default || QRModule;
        const url = await QRCode.toDataURL(payload, { width: 240, margin: 1 });
        if (active) setQrDataUrl(url);
      } catch (_e) {
        if (active) setQrDataUrl("");
      }
    }
    if (profile) gen();
    return () => { active = false; };
  }, [payload, profile]);

  if (error) return <p>{error}</p>;
  if (!profile || !idInfo) return <p>Loading profile...</p>;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", textAlign: "left" }}>
      <h2>My Profile</h2>
      <div style={{ background: "#fff", border: "1px solid #eee", borderRadius: 8, padding: 16 }}>
        <div><b>Username:</b> {profile.user?.username}</div>
        <div><b>Email:</b> {profile.user?.email || ""}</div>
        <div><b>Barangay ID:</b> {profile.barangay_id}</div>
        <div><b>Address:</b> {profile.address}</div>
        <div><b>Birthdate:</b> {profile.birthdate}</div>
        <div><b>Expiry:</b> {profile.expiry_date}</div>
      </div>

      <div className="card" style={{ marginTop: 12, textAlign: "center" }}>
        <h3>Virtual ID (QR)</h3>
        {qrDataUrl ? (
          <img src={qrDataUrl} alt="Resident QR" style={{ width: 240, height: 240 }} />
        ) : (
          <pre style={{ background: "#0f172a", color: "#e2e8f0", padding: 12, borderRadius: 8, overflowX: "auto", textAlign: "left" }}>{payload}</pre>
        )}
        <p style={{ opacity: 0.7 }}>Ensure the QR is clearly visible for scanning.</p>
      </div>
    </div>
  );
}
