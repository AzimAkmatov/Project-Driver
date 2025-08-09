import { useState, useEffect } from "react";
import LoginModal from "./LoginModal.jsx";
import { getCeoToken, getStaffToken, clearTokens, companyMe } from "../api";
import { useNavigate } from "react-router-dom";

export default function NavBar() {
  const [open, setOpen] = useState(false);
  const [companyName, setCompanyName] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const t = getCeoToken();
    if (!t) { setCompanyName(""); return; }
    companyMe(t)
      .then(({ data }) => setCompanyName(data.name || "Company"))
      .catch(() => setCompanyName(""));
  }, [open]);

  const loggedIn = !!getCeoToken() || !!getStaffToken();

  return (
    <div className="w-full bg-white/90 border-b sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img src="https://upload.wikimedia.org/wikipedia/commons/4/46/Steering_wheel_icon.svg" className="w-9 h-9" />
          <span className="text-xl font-semibold text-emerald-700">Safe Driver</span>
        </div>
        <div className="flex items-center gap-4">
          {companyName && <span className="text-sm text-gray-600">Hi, {companyName}</span>}
          {!loggedIn ? (
            <button onClick={() => setOpen(true)} className="px-3 py-1 rounded bg-gray-900 text-white">Log In</button>
          ) : (
            <>
              <button onClick={() => navigate("/app")} className="px-3 py-1 rounded border">Dashboard</button>
              <button
                onClick={() => { clearTokens(); setCompanyName(""); navigate("/"); }}
                className="px-3 py-1 rounded bg-red-600 text-white"
              >
                Log Out
              </button>
            </>
          )}
        </div>
      </div>
      {open && <LoginModal onClose={() => setOpen(false)} />}
    </div>
  );
}
