import { BrowserRouter, Route, Routes } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";
import ProtectedRoute from "./components/common/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import Situations from "./pages/Situations";
import SituationDetails from "./pages/SituationDetails";
import Workflows from "./pages/Workflows";
import WorkflowExecutions from "./pages/WorkflowExecutions";
import WorkflowBuilder from "./pages/WorkflowBuilder";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<Login />}
        />

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route
              path="/"
              element={<Dashboard />}
            />

            <Route
              path="/alerts"
              element={<Alerts />}
            />

            <Route
              path="/situations"
              element={<Situations />}
            />

            <Route
              path="/situations/:id"
              element={<SituationDetails />}
            />

            <Route
              path="/workflows"
              element={<Workflows />}
            />

            <Route
              path="/workflow-executions"
              element={<WorkflowExecutions />}
            />

            {/* <Route
              path="/workflow-builder"
              element={<WorkflowBuilder />}
            /> */}
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}