import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert as MuiAlert,
  Box,
  Chip,
  FormControl,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { Link } from "react-router-dom";

import { getAlerts } from "../api/alerts";

export default function Alerts() {
  const {
    data: alerts = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["alerts"],
    queryFn: getAlerts,
  });

  const [severityFilter, setSeverityFilter] =
    useState("All");

  const [sourceFilter, setSourceFilter] =
    useState("All");

  const filteredAlerts = useMemo(() => {
    return alerts.filter((alert) => {
      const severityMatch =
        severityFilter === "All" ||
        alert.severity.toLowerCase() ===
          severityFilter.toLowerCase();

      const sourceMatch =
        sourceFilter === "All" ||
        alert.source === sourceFilter;

      return severityMatch && sourceMatch;
    });
  }, [
    alerts,
    severityFilter,
    sourceFilter,
  ]);

  const sources = [
    ...new Set(
      alerts.map((alert) => alert.source),
    ),
  ];

  if (isLoading) {
    return <LinearProgress />;
  }

  if (isError) {
    return (
      <MuiAlert severity="error">
        Unable to load alerts.
      </MuiAlert>
    );
  }

  return (
    <Box>
      <Typography
        variant="h4"
        fontWeight={700}
        gutterBottom
      >
        Alerts
      </Typography>

      <Typography
        color="text.secondary"
        sx={{ mb: 3 }}
      >
        Monitor and investigate alerts from
        connected observability platforms.
      </Typography>

      <Box
        sx={{
          display: "flex",
          gap: 2,
          mb: 3,
          flexWrap: "wrap",
        }}
      >
        <FormControl
          size="small"
          sx={{ minWidth: 160 }}
        >
          <InputLabel>Severity</InputLabel>

          <Select
            value={severityFilter}
            label="Severity"
            onChange={(event) =>
              setSeverityFilter(
                event.target.value,
              )
            }
          >
            <MenuItem value="All">
              All
            </MenuItem>

            <MenuItem value="Critical">
              Critical
            </MenuItem>

            <MenuItem value="High">
              High
            </MenuItem>

            <MenuItem value="Medium">
              Medium
            </MenuItem>

            <MenuItem value="Low">
              Low
            </MenuItem>
          </Select>
        </FormControl>

        <FormControl
          size="small"
          sx={{ minWidth: 160 }}
        >
          <InputLabel>Source</InputLabel>

          <Select
            value={sourceFilter}
            label="Source"
            onChange={(event) =>
              setSourceFilter(
                event.target.value,
              )
            }
          >
            <MenuItem value="All">
              All
            </MenuItem>

            {sources.map((source) => (
              <MenuItem
                key={source}
                value={source}
              >
                {source}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <TableContainer
        component={Paper}
        elevation={2}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Alert</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Service</TableCell>
              <TableCell>
                Environment
              </TableCell>
              <TableCell>
                Situation
              </TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {filteredAlerts.map((alert) => (
              <TableRow key={alert.id}>
                <TableCell>
                  {alert.id}
                </TableCell>

                <TableCell>
                  <Typography
                    fontWeight={600}
                  >
                    {alert.title}
                  </Typography>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                  >
                    {alert.description}
                  </Typography>
                </TableCell>

                <TableCell>
                  {alert.source}
                </TableCell>

                <TableCell>
                  <Chip
                    label={alert.severity}
                    size="small"
                  />
                </TableCell>

                <TableCell>
                  <Chip
                    label={alert.status}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>

                <TableCell>
                  {alert.service ?? "—"}
                </TableCell>

                <TableCell>
                  {alert.environment ?? "—"}
                </TableCell>

                <TableCell>
                  {alert.situation_id ? (
                    <Link
                      to={`/situations/${alert.situation_id}`}
                      style={{
                        textDecoration:
                          "none",
                      }}
                    >
                      Situation #
                      {alert.situation_id}
                    </Link>
                  ) : (
                    "Unassigned"
                  )}
                </TableCell>
              </TableRow>
            ))}

            {filteredAlerts.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={8}
                  align="center"
                >
                  No alerts found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}