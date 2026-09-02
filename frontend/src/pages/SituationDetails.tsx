import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert as MuiAlert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";

import {
  analyzeSituation,
  getSituationContext,
  updateSituationStatus,
} from "../api/situations";

export default function SituationDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const situationId = Number(id);

  const [selectedStatus, setSelectedStatus] =
    useState("");

  const {
    data: situation,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["situation-context", situationId],
    queryFn: () =>
      getSituationContext(situationId),
    enabled: Number.isFinite(situationId),
  });

  const statusMutation = useMutation({
    mutationFn: (status: string) =>
      updateSituationStatus(
        situationId,
        status,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["situation-context", situationId],
      });

      queryClient.invalidateQueries({
        queryKey: ["situations"],
      });

      queryClient.invalidateQueries({
        queryKey: ["alerts"],
      });
    },
  });

  const aiMutation = useMutation({
    mutationFn: () =>
      analyzeSituation(situationId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["situation-context", situationId],
      });

      queryClient.invalidateQueries({
        queryKey: ["situations"],
      });
    },
  });

  if (!Number.isFinite(situationId)) {
    return (
      <MuiAlert severity="error">
        Invalid situation ID.
      </MuiAlert>
    );
  }

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (isError || !situation) {
    return (
      <MuiAlert severity="error">
        Unable to load Situation #{situationId}.
        {error instanceof Error
          ? ` ${error.message}`
          : ""}
      </MuiAlert>
    );
  }

  const handleStatusChange = () => {
    if (!selectedStatus) {
      return;
    }

    statusMutation.mutate(selectedStatus);
  };

  return (
    <Box>
      <Button
        onClick={() => navigate("/situations")}
        sx={{ mb: 2 }}
      >
        ← Back to Situations
      </Button>

      <Stack spacing={3}>
        <Card>
          <CardContent>
            <Stack
              direction={{
                xs: "column",
                md: "row",
              }}
              justifyContent="space-between"
              alignItems={{
                xs: "flex-start",
                md: "center",
              }}
              spacing={2}
            >
              <Box>
                <Typography
                  variant="h4"
                  fontWeight={700}
                  gutterBottom
                >
                  {situation.title}
                </Typography>

                <Typography color="text.secondary">
                  Situation #{situation.id}
                </Typography>
              </Box>

              <Stack
                direction="row"
                spacing={1}
                flexWrap="wrap"
              >
                <Chip
                  label={situation.severity}
                  size="medium"
                />

                <Chip
                  label={situation.status}
                  size="medium"
                  variant="outlined"
                />
              </Stack>
            </Stack>

            <Divider sx={{ my: 3 }} />

            <Stack
              direction={{
                xs: "column",
                sm: "row",
              }}
              spacing={4}
              flexWrap="wrap"
            >
              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Service
                </Typography>

                <Typography fontWeight={600}>
                  {situation.service ?? "—"}
                </Typography>
              </Box>

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Environment
                </Typography>

                <Typography fontWeight={600}>
                  {situation.environment ?? "—"}
                </Typography>
              </Box>

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Alerts
                </Typography>

                <Typography fontWeight={600}>
                  {situation.alert_count}
                </Typography>
              </Box>

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Correlation Score
                </Typography>

                <Typography fontWeight={600}>
                  {situation.correlation_score ??
                    "—"}
                </Typography>
              </Box>

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  AI Status
                </Typography>

                <Typography fontWeight={600}>
                  {situation.ai_status}
                </Typography>
              </Box>
            </Stack>

            {situation.description && (
              <>
                <Divider sx={{ my: 3 }} />

                <Typography
                  variant="body1"
                  color="text.secondary"
                >
                  {situation.description}
                </Typography>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography
              variant="h6"
              fontWeight={700}
              gutterBottom
            >
              Correlation Evidence
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 2 }}
            >
              Method:{" "}
              {situation.correlation_method ??
                "—"}
            </Typography>

            <Stack
              direction="row"
              spacing={1}
              flexWrap="wrap"
            >
              {(
                situation.correlation_reasons ??
                []
              ).map((reason) => (
                <Chip
                  key={reason}
                  label={reason}
                  size="small"
                  variant="outlined"
                />
              ))}

              {(
                situation.correlation_reasons ??
                []
              ).length === 0 && (
                <Typography color="text.secondary">
                  No correlation evidence available.
                </Typography>
              )}
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              spacing={2}
              sx={{ mb: 2 }}
            >
              <Typography
                variant="h6"
                fontWeight={700}
              >
                Related Alerts
              </Typography>

              <Chip
                label={`${situation.alerts.length} alerts`}
                size="small"
              />
            </Stack>

            <Stack spacing={2}>
              {situation.alerts.map((alert) => (
                <Box key={alert.id}>
                  <Stack
                    direction={{
                      xs: "column",
                      sm: "row",
                    }}
                    justifyContent="space-between"
                    spacing={2}
                  >
                    <Box>
                      <Typography fontWeight={600}>
                        #{alert.id} — {alert.title}
                      </Typography>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        {alert.source} ·{" "}
                        {alert.service ?? "—"} ·{" "}
                        {alert.environment ?? "—"}
                      </Typography>
                    </Box>

                    <Stack
                      direction="row"
                      spacing={1}
                    >
                      <Chip
                        label={alert.severity}
                        size="small"
                      />

                      <Chip
                        label={alert.source}
                        size="small"
                        variant="outlined"
                      />
                    </Stack>
                  </Stack>

                  <Divider sx={{ mt: 2 }} />
                </Box>
              ))}

              {situation.alerts.length === 0 && (
                <Typography color="text.secondary">
                  No related alerts found.
                </Typography>
              )}
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Stack
              direction={{
                xs: "column",
                md: "row",
              }}
              justifyContent="space-between"
              alignItems={{
                xs: "flex-start",
                md: "center",
              }}
              spacing={2}
              sx={{ mb: 3 }}
            >
              <Box>
                <Typography
                  variant="h6"
                  fontWeight={700}
                >
                  AI Analysis
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                >
                  Generated using Ollama and
                  historical context.
                </Typography>
              </Box>

              <Button
                variant="contained"
                onClick={() =>
                  aiMutation.mutate()
                }
                disabled={aiMutation.isPending}
              >
                {aiMutation.isPending
                  ? "Analyzing..."
                  : "Run AI Analysis"}
              </Button>
            </Stack>

            {aiMutation.isError && (
              <MuiAlert
                severity="error"
                sx={{ mb: 2 }}
              >
                AI analysis failed. Check that
                Ollama is running.
              </MuiAlert>
            )}

            <Stack spacing={3}>
              <Box>
                <Typography
                  variant="subtitle1"
                  fontWeight={700}
                  gutterBottom
                >
                  Summary
                </Typography>

                <Typography
                  whiteSpace="pre-wrap"
                  color={
                    situation.ai_summary
                      ? "text.primary"
                      : "text.secondary"
                  }
                >
                  {situation.ai_summary ??
                    "No AI summary available."}
                </Typography>
              </Box>

              <Divider />

              <Box>
                <Typography
                  variant="subtitle1"
                  fontWeight={700}
                  gutterBottom
                >
                  Probable Root Cause
                </Typography>

                <Typography
                  whiteSpace="pre-wrap"
                  color={
                    situation.ai_root_cause
                      ? "text.primary"
                      : "text.secondary"
                  }
                >
                  {situation.ai_root_cause ??
                    "No root-cause analysis available."}
                </Typography>
              </Box>

              <Divider />

              <Box>
                <Typography
                  variant="subtitle1"
                  fontWeight={700}
                  gutterBottom
                >
                  Recommended Actions
                </Typography>

                <Typography
                  whiteSpace="pre-wrap"
                  color={
                    situation.ai_recommendations
                      ? "text.primary"
                      : "text.secondary"
                  }
                >
                  {situation.ai_recommendations ??
                    "No recommendations available."}
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography
              variant="h6"
              fontWeight={700}
              gutterBottom
            >
              Situation Lifecycle
            </Typography>

            <Stack
              direction={{
                xs: "column",
                sm: "row",
              }}
              spacing={2}
              alignItems={{
                xs: "stretch",
                sm: "center",
              }}
            >
              <FormControl
                size="small"
                sx={{ minWidth: 200 }}
              >
                <InputLabel>
                  New Status
                </InputLabel>

                <Select
                  value={selectedStatus}
                  label="New Status"
                  onChange={(event) =>
                    setSelectedStatus(
                      event.target.value,
                    )
                  }
                >
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

              <Button
                variant="outlined"
                onClick={handleStatusChange}
                disabled={
                  !selectedStatus ||
                  statusMutation.isPending
                }
              >
                {statusMutation.isPending
                  ? "Updating..."
                  : "Update Status"}
              </Button>
            </Stack>

            {statusMutation.isError && (
              <MuiAlert
                severity="error"
                sx={{ mt: 2 }}
              >
                Unable to update the Situation
                status.
              </MuiAlert>
            )}

            {statusMutation.isSuccess && (
              <MuiAlert
                severity="success"
                sx={{ mt: 2 }}
              >
                Situation status updated
                successfully.
              </MuiAlert>
            )}
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}