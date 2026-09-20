import {
  AppBar,
  Box,
  FormControlLabel,
  Switch,
  Toolbar,
  Typography,
} from "@mui/material";
import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import { useAppTheme } from "../../theme/useAppTheme";

export default function AppLayout() {
  const { mode, toggleTheme } = useAppTheme();

  return (
    <Box
      sx={{
        display: "flex",
        minHeight: "100vh",
        bgcolor: "background.default",
      }}
    >
      <Sidebar />

      <Box
        sx={{
          flex: 1,
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <AppBar
          position="sticky"
          color="inherit"
          elevation={0}
        >
          <Toolbar
            sx={{
              minHeight: 64,
              px: { xs: 2, md: 3 },
            }}
          >
            <Typography
              variant="h6"
              sx={{
                fontWeight: 800,
                letterSpacing: "-0.02em",
              }}
            >
              CogniOpsAI
            </Typography>

            <Box sx={{ flex: 1 }} />

            <FormControlLabel
              sx={{ m: 0 }}
              control={
                <Switch
                  checked={mode === "dark"}
                  onChange={toggleTheme}
                  size="small"
                  inputProps={{
                    "aria-label": "Toggle dark mode",
                  }}
                />
              }
              label={mode === "dark" ? "Dark" : "Light"}
            />
          </Toolbar>
        </AppBar>

        <Box
          component="main"
          sx={{
            flex: 1,
            width: "100%",
            px: { xs: 2, sm: 3, lg: 4 },
            py: { xs: 2, sm: 3, lg: 4 },
          }}
        >
          <Box
            sx={{
              width: "100%",
              maxWidth: 1440,
              mx: "auto",
            }}
          >
            <Outlet />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
