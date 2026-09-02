import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert as MuiAlert,
  Box,
  Button,
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

import { getSituations } from "../api/situations";

export default function Situations() {
  const {
    data: situations = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["situations"],
    queryFn: getSituations,
  });

  const [statusFilter, setStatusFilter] =
    useState("All");

  const [severityFilter, setSeverityFilter] =
    useState("All");

  const filteredSituations = useMemo(() => {
    return situations.filter((situation) => {
      const statusMatch =
        statusFilter === "All" ||
        situation.status.toLowerCase() ===
          statusFilter.toLowerCase();

      const severityMatch =
        severityFilter === "All" ||
        situation.severity.toLowerCase() ===
          severityFilter.toLowerCase();

      return statusMatch && severityMatch;
    });
  }, [
    situations,
    statusFilter,
    severityFilter,
  ]);

  if (isLoading) {
    return <LinearProgress />;
  }

  if (isError) {
    return (
      <MuiAlert severity="error">
        Unable to load situations.
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
        Situations
      </Typography>

      <Typography
        color="text.secondary"
        sx={{ mb: 3 }}
      >
        Correlated operational incidents and their
        current AI-assisted analysis.
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
          sx={{ minWidth: 170 }}
        >
          <InputLabel>Status</InputLabel>

          <Select
            value={statusFilter}
            label="Status"
            onChange={(event) =>
              setStatusFilter(
                event.target.value,
              )
            }
          >
            <MenuItem value="All">
              All
            </MenuItem>

            <MenuItem value="Open">
              Open
            </MenuItem>

            <MenuItem value="Investigating">
              Investigating
            </MenuItem>

            <MenuItem value="Resolved">
              Resolved
            </MenuItem>
          </Select>
        </FormControl>

        <FormControl
          size="small"
          sx={{ minWidth: 170 }}
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
      </Box>

      <TableContainer
        component={Paper}
        elevation={2}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Situation</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Service</TableCell>
              <TableCell>
                Environment
              </TableCell>
              <TableCell align="center">
                Alerts
              </TableCell>
              <TableCell>
                Correlation
              </TableCell>
              <TableCell>
                AI Status
              </TableCell>
              <TableCell />
            </TableRow>
          </TableHead>

          <TableBody>
            {filteredSituations.map(
              (situation) => (
                <TableRow
                  key={situation.id}
                  hover
                >
                  <TableCell>
                    #{situation.id}
                  </TableCell>

                  <TableCell>
                    <Typography
                      fontWeight={600}
                    >
                      {situation.title}
                    </Typography>

                    <Typography
                      variant="body2"
                      color="text.secondary"
                    >
                      {situation.description ??
                        "No description"}
                    </Typography>
                  </TableCell>

                  <TableCell>
                    <Chip
                      label={situation.severity}
                      size="small"
                    />
                  </TableCell>

                  <TableCell>
                    <Chip
                      label={situation.status}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>

                  <TableCell>
                    {situation.service ?? "—"}
                  </TableCell>

                  <TableCell>
                    {situation.environment ??
                      "—"}
                  </TableCell>

                  <TableCell align="center">
                    {situation.alert_count}
                  </TableCell>

                  <TableCell>
                    {situation.correlation_score !=
                    null
                      ? situation.correlation_score
                      : "—"}
                  </TableCell>

                  <TableCell>
                    <Chip
                      label={
                        situation.ai_status
                      }
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>

                  <TableCell>
                    <Button
                      component={Link}
                      to={`/situations/${situation.id}`}
                      size="small"
                      variant="outlined"
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ),
            )}

            {filteredSituations.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={10}
                  align="center"
                >
                  No situations found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}