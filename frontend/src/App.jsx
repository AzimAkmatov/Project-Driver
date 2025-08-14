import { useState } from "react";
import {
  ping, loginCEO, inviteStaff, loginStaff,
  createDriver, searchDrivers, rateDriver, getDriverRatings
} from "./api";

export default function App() {
  const [ceoToken, setCeoToken] = useState("");
  const [staffToken, setStaffToken] = useState("");
  const [driverId, setDriverId] = useState("");
  const [log, setLog] = useState([]);

  const addLog = (msg) => setLog((l) => [`• ${msg}`, ...l]);

  const doPing = async () => {
    const { data } = await ping();
    addLog(`Ping: ${JSON.stringify(data)}`);
  };

  const doCeoLogin = async () => {
    const { data } = await loginCEO("ceo@acme.com", "Secret123!");
    setCeoToken(data.access_token);
    addLog("CEO logged in");
  };

  const doInviteStaff = async () => {
    await inviteStaff(ceoToken, {
      name: "Sara Dispatch",
      email: "dispatch@acme.com",
      department: "dispatch",
    }).catch(() => {});
    addLog("Invited staff (or already exists)");
  };

  const doStaffLogin = async () => {
    const { data } = await loginStaff("dispatch@acme.com", "changeme123");
    setStaffToken(data.access_token);
    addLog("Staff logged in");
  };

  const doCreateDriver = async () => {
    const { data } = await createDriver(ceoToken, {
      name: "John Doe",
      dob: "1990-01-15",
      license_number: "D1234567",
    }).catch(async (e) => {
      // If exists, just fetch it
      const res = await searchDrivers(ceoToken, "John");
      return { data: res.data[0] };
    });
    setDriverId(data.id);
    addLog(`Driver ready: #${data.id}`);
  };

  const doRate = async () => {
    await rateDriver(staffToken, { driver_id: Number(driverId), score: 5, comment: "On-time, professional" });
    addLog("Rated driver 5");
  };

  const doGetRatings = async () => {
    const { data } = await getDriverRatings(ceoToken, Number(driverId));
    addLog(`Ratings: ${JSON.stringify(data)}`);
    alert(JSON.stringify(data, null, 2));
  };

  return (
    <div className="min-h-screen p-6 space-y-4 bg-gray-50">
      <h1 className="text-2xl font-bold">Driver Demo</h1>

      <div className="grid gap-3 md:grid-cols-2">
        <div className="p-4 bg-white rounded-xl shadow space-y-2">
          <h2 className="font-semibold">API Actions</h2>
          <div className="flex flex-wrap gap-2">
            <button className="px-3 py-1 bg-gray-800 text-white rounded" onClick={doPing}>Ping</button>
            <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={doCeoLogin}>Login CEO</button>
            <button className="px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-50" disabled={!ceoToken} onClick={doInviteStaff}>Invite Staff</button>
            <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={doStaffLogin}>Login Staff</button>
            <button className="px-3 py-1 bg-green-600 text-white rounded disabled:opacity-50" disabled={!ceoToken} onClick={doCreateDriver}>Create/Find Driver</button>
            <button className="px-3 py-1 bg-purple-600 text-white rounded disabled:opacity-50" disabled={!staffToken || !driverId} onClick={doRate}>Rate Driver</button>
            <button className="px-3 py-1 bg-indigo-600 text-white rounded disabled:opacity-50" disabled={!ceoToken || !driverId} onClick={doGetRatings}>Get Ratings</button>
          </div>
        </div>

        <div className="p-4 bg-white rounded-xl shadow">
          <h2 className="font-semibold mb-2">Log</h2>
          <div className="text-sm space-y-1">
            {log.map((l, i) => <div key={i}>{l}</div>)}
          </div>
        </div>
      </div>
    </div>
  );
}
