import { Routes, Route, Link, useLocation } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import DebatePage from "./pages/DebatePage.jsx";
import HistoryPage from "./pages/HistoryPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";

export default function App() {
  const location = useLocation();

  return (
    <div className="app">
      <header className="header">
        <Link to="/" className="logo">
          AutoDebater
        </Link>
        <nav>
          <Link
            to="/"
            className={location.pathname === "/" ? "active" : ""}
          >
            New Debate
          </Link>
          <Link
            to="/history"
            className={location.pathname === "/history" ? "active" : ""}
          >
            History
          </Link>
          <Link
            to="/profile"
            className={location.pathname === "/profile" ? "active" : ""}
          >
            Profile
          </Link>
        </nav>
      </header>

      <main className="main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/debate/:debateId" element={<DebatePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </main>
    </div>
  );
}
