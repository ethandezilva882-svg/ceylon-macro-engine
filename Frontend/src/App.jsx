import { BrowserRouter, Routes, Route, NavLink, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Placeholder from "./pages/Placeholder";

export default function App() {
  return (
    <BrowserRouter>
      <header className="site-header">
        <div className="container">
          <Link to="/" className="brand">Ceylon Cost of Living</Link>
          <nav className="nav" aria-label="Main">
            <NavLink to="/" end>Dashboard</NavLink>
            <NavLink to="/macro">Macro</NavLink>
            <NavLink to="/correlation">Correlation</NavLink>
            <NavLink to="/events">Events</NavLink>
            <NavLink to="/login">Login</NavLink>
          </nav>
        </div>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/macro" element={<Placeholder title="Macro Explorer" />} />
          <Route path="/correlation" element={<Placeholder title="Correlation" />} />
          <Route path="/events" element={<Placeholder title="Events" />} />
          <Route path="/basket" element={<Placeholder title="Basket Builder" />} />
          <Route path="/login" element={<Placeholder title="Login" />} />
          <Route path="/register" element={<Placeholder title="Register" />} />
        </Routes>
      </main>

      <footer className="site-footer">
        <div className="container">
          <span>Data source: Central Bank of Sri Lanka (CBSL)</span>
          <a href="https://github.com/ethandezilva882-svg/ceylon-macro-engine">GitHub</a>
          <span>For educational purposes only, not financial advice.</span>
        </div>
      </footer>
    </BrowserRouter>
  );
}
