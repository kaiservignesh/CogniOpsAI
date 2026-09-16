import { Link as RouterLink } from "react-router-dom";
import { useMemo, useState } from "react";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  Alert as MuiAlert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";

import {
  createCorrelationPolicy,
  getCorrelationPolicies,
  updateCorrelationPolicy,
} from "../api/correlationPolicies";

export default function CorrelationWorkflows() {
  const queryClient =
    useQueryClient();

  const [jsonOpen, setJsonOpen] =
    useState(false);

  const [jsonText, setJsonText] =
    useState(`{
  "name": "",
  "description": "",
  "enabled": true,
  "condition": {
    "match": "all",
    "rules": [
      {
        "field": "source",
        "operator": "equals",
        "value": "Grafana"
      }
    ]
  },
  "time_window_minutes": 5
}`);

  const [jsonError, setJsonError] =
    useState("");

  const {
    data: policies = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: [
      "correlation-policies",
    ],
    queryFn:
      getCorrelationPolicies,
  });

  const createMutation =
    useMutation({
      mutationFn:
        createCorrelationPolicy,

      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: [
            "correlation-policies",
          ],
        });

        setJsonOpen(false);
      },
    });

  const updateMutation =
    useMutation({
      mutationFn: ({
        id,
        enabled,
      }: {
        id: number;
        enabled: boolean;
      }) =>
        updateCorrelationPolicy(
          id,
          { enabled },
        ),

      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: [
            "correlation-policies",
          ],
        });
      },
    });

  const orderedPolicies =
    useMemo(
      () =>
        [...policies].sort(
          (a, b) =>
            new Date(
              b.created_at,
            ).getTime() -
            new Date(
              a.created_at,
            ).getTime(),
        ),
      [policies],
    );

  const handleCreateJson =
    () => {
      setJsonError("");

      try {
        const parsed =
          JSON.parse(jsonText);

        if (
          !parsed.name?.trim()
        ) {
          setJsonError(
            "Name is required.",
          );
          return;
        }

        if (
          !parsed.condition
            ?.rules?.length
        ) {
          setJsonError(
            "At least one condition rule is required.",
          );
          return;
        }

        createMutation.mutate({
          name:
            parsed.name.trim(),

          description:
            parsed.description
              ?.trim() || undefined,

          enabled:
            parsed.enabled ??
            true,

          condition:
            parsed.condition,

          time_window_minutes:
            Math.max(
              1,
              Number(
                parsed.time_window_minutes ??
                  5,
              ),
            ),
        });
      } catch {
        setJsonError(
          "Invalid JSON.",
        );
      }
    };

  if (isLoading) {
    return (
      <Typography>
        Loading correlation workflows...
      </Typography>
    );
  }

  if (isError) {
    return (
      <MuiAlert severity="error">
        Unable to load correlation workflows.
      </MuiAlert>
    );
  }

  return (
    <Box>
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
            variant="h4"
            fontWeight={700}
          >
            Correlation Workflows
          </Typography>

          <Typography color="text.secondary">
            Define and manage rules used to
            group alerts into Situations.
          </Typography>
        </Box>

        <Stack
          direction={{
            xs: "column",
            sm: "row",
          }}
          spacing={1}
        >
          <Button
            component={RouterLink}
            to="/correlation-workflow-builder"
            variant="outlined"
          >
            Correlation Workflow Builder
          </Button>

          <Button
            variant="contained"
            onClick={() => {
              setJsonError("");
              setJsonOpen(true);
            }}
          >
            Create Correlation Policy
          </Button>
        </Stack>
      </Stack>

      {updateMutation.isError && (
        <MuiAlert
          severity="error"
          sx={{ mb: 2 }}
        >
          Failed to update correlation workflow.
        </MuiAlert>
      )}

      <TableContainer
        component={Paper}
        elevation={2}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                ID
              </TableCell>

              <TableCell>
                Workflow
              </TableCell>

              <TableCell>
                Rules
              </TableCell>

              <TableCell>
                Time Window
              </TableCell>

              <TableCell>
                Status
              </TableCell>

              <TableCell align="right">
                Actions
              </TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {orderedPolicies.map(
              (policy) => {
                const rules =
                  policy.condition
                    ?.rules ?? [];

                const match =
                  policy.condition
                    ?.match ?? "all";

                return (
                  <TableRow
                    key={policy.id}
                    hover
                  >
                    <TableCell>
                      #{policy.id}
                    </TableCell>

                    <TableCell>
                      <Typography fontWeight={600}>
                        {policy.name}
                      </Typography>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        {policy.description ||
                          "No description"}
                      </Typography>
                    </TableCell>

                    <TableCell>
                      <Typography
                        variant="body2"
                        fontWeight={600}
                      >
                        {rules.length}{" "}
                        rule
                        {rules.length ===
                        1
                          ? ""
                          : "s"}{" "}
                        ({match})
                      </Typography>

                      {rules
                        .slice(0, 3)
                        .map(
                          (
                            rule,
                            index,
                          ) => (
                            <Typography
                              key={`${policy.id}-${index}`}
                              variant="caption"
                              display="block"
                              color="text.secondary"
                            >
                              {
                                rule.field
                              }{" "}
                              {
                                rule.operator
                              }{" "}
                              "
                              {
                                rule.value
                              }
                              "
                            </Typography>
                          ),
                        )}

                      {rules.length >
                        3 && (
                        <Typography
                          variant="caption"
                          color="text.secondary"
                        >
                          +
                          {rules.length -
                            3}{" "}
                          more
                        </Typography>
                      )}
                    </TableCell>

                    <TableCell>
                      {
                        policy.time_window_minutes
                      }{" "}
                      min
                    </TableCell>

                    <TableCell>
                      <Chip
                        label={
                          policy.enabled
                            ? "Enabled"
                            : "Disabled"
                        }
                        color={
                          policy.enabled
                            ? "success"
                            : "default"
                        }
                        size="small"
                      />
                    </TableCell>

                    <TableCell align="right">
                      <Stack
                        direction="row"
                        spacing={1}
                        justifyContent="flex-end"
                      >
                        <Button
                          size="small"
                          variant="outlined"
                          component={
                            RouterLink
                          }
                          to={`/correlation-workflow-builder/${policy.id}`}
                        >
                          Edit
                        </Button>

                        <Button
                          size="small"
                          onClick={() =>
                            updateMutation.mutate(
                              {
                                id:
                                  policy.id,
                                enabled:
                                  !policy.enabled,
                              },
                            )
                          }
                          disabled={
                            updateMutation.isPending
                          }
                        >
                          {policy.enabled
                            ? "Disable"
                            : "Enable"}
                        </Button>
                      </Stack>
                    </TableCell>
                  </TableRow>
                );
              },
            )}

            {orderedPolicies.length ===
              0 && (
              <TableRow>
                <TableCell
                  colSpan={6}
                  align="center"
                >
                  No correlation workflows
                  found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={jsonOpen}
        onClose={() =>
          setJsonOpen(false)
        }
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          Create Correlation Policy
          from JSON
        </DialogTitle>

        <DialogContent>
          <TextField
            sx={{ mt: 1 }}
            fullWidth
            multiline
            minRows={18}
            value={jsonText}
            onChange={(event) =>
              setJsonText(
                event.target.value,
              )
            }
            inputProps={{
              style: {
                fontFamily:
                  "monospace",
              },
            }}
          />

          {jsonError && (
            <MuiAlert
              severity="error"
              sx={{ mt: 2 }}
            >
              {jsonError}
            </MuiAlert>
          )}

          {createMutation.isError && (
            <MuiAlert
              severity="error"
              sx={{ mt: 2 }}
            >
              Failed to create correlation policy.
            </MuiAlert>
          )}
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() =>
              setJsonOpen(false)
            }
          >
            Cancel
          </Button>

          <Button
            variant="contained"
            onClick={
              handleCreateJson
            }
            disabled={
              createMutation.isPending
            }
          >
            {createMutation.isPending
              ? "Creating..."
              : "Create Policy"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}