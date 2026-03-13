// ─── src/App.js ───────────────────────────────────────────────────────────────
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout       from "./components/layout/Layout";
import Dashboard    from "./pages/Dashboard";
import Districts    from "./pages/Districts";
import FloodEvents  from "./pages/FloodEvents";
import Simulation   from "./pages/Simulation";
import Results      from "./pages/Results";
import DataIngestion from "./pages/DataIngestion";
import CaseStudy    from "./pages/CaseStudy";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/"             element={<Dashboard />} />
          <Route path="/districts"    element={<Districts />} />
          <Route path="/flood-events" element={<FloodEvents />} />
          <Route path="/simulation"   element={<Simulation />} />
          <Route path="/results/:id"  element={<Results />} />
          <Route path="/data"         element={<DataIngestion />} />
          <Route path="/case-study"   element={<CaseStudy />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};
