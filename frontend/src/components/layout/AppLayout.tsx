import {
  AppBar,
  Box,
  Toolbar,
  Typography,
} from "@mui/material";
import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";

export default function AppLayout() {
  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />

      <Box sx={{ flex: 1 }}>
        <AppBar
          position="static"
          color="inherit"
          elevation={1}
        >
          <Toolbar>
            <Typography
              variant="h6"
              fontWeight={700}
            >
              CogniOpsAI
            </Typography>
          </Toolbar>
        </AppBar>

        <Box sx={{ p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}