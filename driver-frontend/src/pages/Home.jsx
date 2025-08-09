import NavBar from "../components/NavBar.jsx";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="max-w-5xl mx-auto px-4 py-12">
        <section className="bg-white rounded-2xl shadow p-10 text-center">
          <h1 className="text-3xl font-bold text-emerald-700">Why DriveSafe?</h1>
          <p className="mt-4 text-gray-600 max-w-2xl mx-auto">
            It provides unique info you can’t get from other platforms. Search company drivers,
            view their ratings from your staff, and keep your fleet safe.
          </p>
          <div className="mt-8">
            <img
              className="mx-auto w-24 opacity-80"
              src="https://upload.wikimedia.org/wikipedia/commons/4/46/Steering_wheel_icon.svg"
            />
          </div>
        </section>
      </main>
    </div>
  );
}
