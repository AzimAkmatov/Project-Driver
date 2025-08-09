import { useState } from "react";
import { loginCEO, loginStaff, setCeoToken, setStaffToken } from "../api";

export default function LoginModal({ onClose }) {
  const [tab, setTab] = useState("ceo");
  const [email, setEmail] = useState(tab === "ceo" ? "ceo@acme.com" : "dispatch@acme.com");
  const [password, setPassword] = useState(tab === "ceo" ? "Secret123!" : "changeme123");
  const [err, setErr] = useState("");

  const switchTab = (t) => {
    setTab(t);
    setErr("");
    if (t === "ceo") { setEmail("ceo@acme.com"); setPassword("Secret123!"); }
    else { setEmail("dispatch@acme.com"); setPassword("changeme123"); }
  };

  const doLogin = async () => {
    setErr("");
    try {
      if (tab === "ceo") {
        const { data } = await loginCEO(email, password);
        setCeoToken(data.access_token);
      } else {
        const { data } = await loginStaff(email, password);
        setStaffToken(data.access_token);
      }
      onClose();
    } catch (e) {
      setErr("Invalid credentials");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md p-5 space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Log In</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-black">✕</button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => switchTab("ceo")}
            className={`px-3 py-1 rounded ${tab==='ceo'?'bg-gray-900 text-white':'border'}`}
          >CEO</button>
          <button
            onClick={() => switchTab("staff")}
            className={`px-3 py-1 rounded ${tab==='staff'?'bg-gray-900 text-white':'border'}`}
          >Staff</button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-sm text-gray-600">Email</label>
            <input className="w-full border rounded px-3 py-2"
              value={email} onChange={e=>setEmail(e.target.value)} />
          </div>
          <div>
            <label className="text-sm text-gray-600">Password</label>
            <input type="password" className="w-full border rounded px-3 py-2"
              value={password} onChange={e=>setPassword(e.target.value)} />
          </div>
          {err && <div className="text-sm text-red-600">{err}</div>}
          <button onClick={doLogin} className="w-full px-3 py-2 rounded bg-emerald-600 text-white">
            Log In
          </button>
        </div>

        <p className="text-xs text-gray-500">
          Tip: default demo users are prefilled for quick login.
        </p>
      </div>
    </div>
  );
}
