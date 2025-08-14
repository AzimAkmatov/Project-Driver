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
      .then(({ data }) => setCompanyName(data?.name || "Company"))
      .catch(() => setCompanyName(""));
  }, [open]);

  const loggedIn = !!getCeoToken() || !!getStaffToken();

  return (
    <div className="w-full bg-white/90 backdrop-blur border-b sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Brand */}
        <button
          className="flex items-center gap-3 select-none"
          onClick={() => navigate("/")}
          aria-label="Go to Home"
        >
          <img
            src="/logo.png"
            alt="Safe Driver logo"
            className="w-10 h-10 object-contain"
            draggable="false"
          />
          <span className="text-2xl font-bold tracking-tight text-emerald-700">
            Safe Driver
          </span>
        </button>

        {/* Right controls */}
        <div className="flex items-center gap-3">
          {companyName && (
            <span className="hidden sm:inline text-sm text-gray-600">
              Hi, {companyName}
            </span>
          )}

          {!loggedIn ? (
            <button
              onClick={() => setOpen(true)}
              className="px-4 py-2 rounded-lg bg-gray-900 text-white hover:bg-gray-800 transition"
            >
              Log In
            </button>
          ) : (
            <>
              <button
                onClick={() => navigate("/app")}
                className="px-4 py-2 rounded-lg border hover:bg-gray-50 transition"
              >
                Dashboard
              </button>
              <button
                onClick={() => {
                  clearTokens();
                  setCompanyName("");
                  navigate("/");
                }}
                className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition"
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
