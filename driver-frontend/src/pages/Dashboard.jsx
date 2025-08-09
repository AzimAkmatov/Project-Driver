import { useEffect, useState } from "react";
import NavBar from "../components/NavBar.jsx";
import {
  getCeoToken, getStaffToken, searchDrivers, getDriverRatings, rateDriver
} from "../api";

export default function Dashboard() {
  const [query, setQuery] = useState("");
  const [driver, setDriver] = useState(null);
  const [ratings, setRatings] = useState([]);
  const [score, setScore] = useState(5);
  const [comment, setComment] = useState("");
  const [msg, setMsg] = useState("");

  const ceoToken = getCeoToken();
  const staffToken = getStaffToken();

  useEffect(() => { setMsg(""); }, [driver]);

  const doSearch = async () => {
    setMsg("");
    try {
      const { data } = await searchDrivers(ceoToken, query);
      setDriver(data?.[0] || null);
      if (!data?.length) setMsg("No drivers found.");
    } catch {
      setMsg("You must be logged in as CEO to search.");
    }
  };

  const pullInfo = async () => {
    if (!driver) return;
    try {
      const { data } = await getDriverRatings(ceoToken, driver.id);
      setRatings(Array.isArray(data) ? data : [data]); // API returns list
    } catch {
      setMsg("Failed to load ratings.");
    }
  };

  const submitRating = async () => {
    if (!driver) return;
    try {
      await rateDriver(staffToken, { driver_id: driver.id, score: Number(score), comment });
      setComment("");
      setScore(5);
      await pullInfo();
      setMsg("Driver rated successfully.");
    } catch {
      setMsg("You must be logged in as Staff to rate.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="max-w-5xl mx-auto px-4 py-8 space-y-6">
        {/* Search */}
        <div className="bg-white rounded-2xl shadow p-5">
          <h2 className="text-lg font-semibold mb-3">Search for the Driver</h2>
          <div className="flex gap-2">
            <input
              className="flex-1 border rounded px-3 py-2"
              placeholder="Type driver name (e.g., John)"
              value={query} onChange={e=>setQuery(e.target.value)}
            />
            <button className="px-4 py-2 rounded bg-gray-900 text-white" onClick={doSearch}>Search</button>
          </div>
          {msg && <div className="mt-3 text-sm text-gray-600">{msg}</div>}
        </div>

        {/* Result + Actions */}
        {driver && (
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold">Driver</h3>
              <div className="mt-2 text-sm">
                <div><span className="text-gray-500">Name:</span> {driver.name}</div>
                <div><span className="text-gray-500">DOB:</span> {driver.dob}</div>
                <div><span className="text-gray-500">License #:</span> {driver.license_number}</div>
                <div><span className="text-gray-500">ID:</span> {driver.id}</div>
              </div>
              <div className="mt-4">
                <button onClick={pullInfo} className="px-3 py-2 rounded bg-emerald-600 text-white">
                  Pull Info (Ratings)
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow p-5">
              <h3 className="font-semibold">Rate Driver</h3>
              <div className="mt-3 flex items-center gap-3">
                <label className="text-sm text-gray-600">Score</label>
                <select value={score} onChange={e=>setScore(e.target.value)} className="border rounded px-2 py-1">
                  {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
              <textarea
                className="mt-3 w-full border rounded px-3 py-2"
                placeholder="Comment"
                value={comment} onChange={e=>setComment(e.target.value)}
              />
              <button onClick={submitRating} className="mt-3 px-3 py-2 rounded bg-purple-600 text-white">
                Submit Rating
              </button>
              <p className="mt-2 text-xs text-gray-500">Staff login required to rate.</p>
            </div>
          </div>
        )}

        {/* Ratings list */}
        {ratings.length > 0 && (
          <div className="bg-white rounded-2xl shadow p-5">
            <h3 className="font-semibold mb-2">Ratings</h3>
            <div className="space-y-2">
              {ratings.map(r => (
                <div key={r.id} className="border rounded p-3 text-sm flex justify-between">
                  <div>
                    <div className="font-medium">Score: {r.score}</div>
                    <div className="text-gray-600">{r.comment || "No comment"}</div>
                  </div>
                  <div className="text-gray-500">Dept: {r.department}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
