import { useMemo, useState, type ReactNode } from "react";
import {
  CssBaseline,
  ThemeProvider,
  createTheme,
} from "@mui/material";

import {
  AppThemeContext,
  type ThemeMode,
} from "./AppThemeContext";

function getInitialMode(): ThemeMode {
  const saved = localStorage.getItem("cogniops-theme");

  if (saved === "light" || saved === "dark") {
    return saved;
  }

  return window.matchMedia?.("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

export function AppThemeProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [mode, setMode] = useState<ThemeMode>(getInitialMode);

  const toggleTheme = () => {
    setMode((current) => {
      const next = current === "light" ? "dark" : "light";
      localStorage.setItem("cogniops-theme", next);
      return next;
    });
  };

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: mode === "dark" ? "#60a5fa" : "#2563eb",
          },
          secondary: {
            main: mode === "dark" ? "#2dd4bf" : "#0f766e",
          },
          background:
            mode === "dark"
              ? {
                  default: "#0b1220",
                  paper: "#111827",
                }
              : {
                  default: "#f5f7fb",
                  paper: "#ffffff",
                },
          divider:
            mode === "dark"
              ? "rgba(148, 163, 184, 0.18)"
              : "rgba(15, 23, 42, 0.10)",
        },
        typography: {
          fontFamily:
            '"Segoe UI", Roboto, Helvetica, Arial, sans-serif',
          h4: {
            fontWeight: 700,
            letterSpacing: "-0.02em",
          },
          h6: {
            fontWeight: 700,
          },
        },
        shape: {
          borderRadius: 10,
        },
        components: {
          MuiCssBaseline: {
            styleOverrides: {
              body: {
                minHeight: "100vh",
                margin: 0,
              },
              "#root": {
                minHeight: "100vh",
              },
            },
          },
          MuiAppBar: {
            styleOverrides: {
              root: {
                backgroundImage: "none",
                borderBottom: "1px solid",
                borderColor:
                  mode === "dark"
                    ? "rgba(148, 163, 184, 0.18)"
                    : "rgba(15, 23, 42, 0.08)",
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                border: "1px solid",
                borderColor:
                  mode === "dark"
                    ? "rgba(148, 163, 184, 0.16)"
                    : "rgba(15, 23, 42, 0.08)",
                boxShadow:
                  mode === "dark"
                    ? "0 8px 24px rgba(0, 0, 0, 0.22)"
                    : "0 6px 18px rgba(15, 23, 42, 0.06)",
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: "none",
              },
            },
          },
          MuiButton: {
            styleOverrides: {
              root: {
                borderRadius: 8,
                textTransform: "none",
                fontWeight: 600,
              },
            },
          },
          MuiChip: {
            styleOverrides: {
              root: {
                fontWeight: 600,
              },
            },
          },
          MuiTableCell: {
            styleOverrides: {
              head: {
                fontWeight: 700,
                backgroundColor:
                  mode === "dark"
                    ? "rgba(148, 163, 184, 0.08)"
                    : "rgba(15, 23, 42, 0.03)",
              },
              root: {
                verticalAlign: "top",
                borderColor:
                  mode === "dark"
                    ? "rgba(148, 163, 184, 0.14)"
                    : "rgba(15, 23, 42, 0.08)",
              },
            },
          },
        },
      }),
    [mode],
  );

  const value = useMemo(
    () => ({ mode, toggleTheme }),
    [mode],
  );

  return (
    <AppThemeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </AppThemeContext.Provider>
  );
}

