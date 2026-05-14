import { createBrowserRouter } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import DistrictMonitor from "./pages/DistrictMonitor";
import WarehouseMonitor from "./pages/WarehouseMonitor";
import SimulationPage from "./pages/SimulationPage";
import AllocationView from "./pages/AllocationView";
import PublicPortal from "./pages/PublicPortal";
import RequestsView from "./pages/RequestsView";
import Settings from "./pages/Settings";

export const router = createBrowserRouter([
  {
    element: <MainLayout />,
    children: [
      {
        path: "/",
        element: <Dashboard />,
      },
      {
        path: "/districts",
        element: <DistrictMonitor />,
      },
      {
        path: "/warehouses",
        element: <WarehouseMonitor />,
      },
      {
        path: "/simulation",
        element: <SimulationPage />,
      },
      {
        path: "/allocations",
        element: <AllocationView />,
      },
      {
        path: "/requests",
        element: <RequestsView />,
      },
      {
        path: "/portal",
        element: <PublicPortal />,
      },
      {
        path: "/settings",
        element: <Settings />,
      },
    ]
  },
  {
    path: "/login",
    element: <Login />,
  },
]);
