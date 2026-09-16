import {
  Link as RouterLink,
  useNavigate,
} from "react-router-dom";
import {
  useState,
} from "react";

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
  createWorkflowPolicy,
  getWorkflowPolicies,
  updateWorkflowPolicy,
} from "../api/workflows";

interface PolicyForm {
  name: string; 
  description: string;
  enabled: boolean;
  condition: string;
  action: string;
}

const emptyForm: PolicyForm = {
  name: "",
  description: "",
  enabled: true,
  condition: JSON.stringify(
    {
      severity: "Critical",
    },
    null,
    2,
  ),
  action: JSON.stringify(
    {
      type: "email",
      target: "operations",
    },
    null,
    2,
  ),
};

export default function Workflows() {

  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const {
    data: policies = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["workflow-policies"],
    queryFn: getWorkflowPolicies,
  });

  const [dialogOpen, setDialogOpen] =
    useState(false);

  const [editingId, setEditingId] =
    useState<number | null>(null);

  const [form, setForm] =
    useState<PolicyForm>(emptyForm);

  const [formError, setFormError] =
    useState("");

  const createMutation = useMutation({
    mutationFn: createWorkflowPolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["workflow-policies"],
      });

      closeDialog();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      policy,
    }: {
      id: number;
      policy: Partial<{
        name: string;
        description: string;
        enabled: boolean;
        condition: Record<string, unknown>;
        action: Record<string, unknown>;
      }>;
    }) =>
      updateWorkflowPolicy(
        id,
        policy,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["workflow-policies"],
      });

      closeDialog();
    },
  });

  const closeDialog = () => {
    setDialogOpen(false);
    setEditingId(null);
    setForm(emptyForm);
    setFormError("");
  };

  const openCreate = () => {
    setEditingId(null);
    setForm(emptyForm);
    setFormError("");
    setDialogOpen(true);
  };

  const openEdit = (
    policy: (typeof policies)[number],
  ) => {
    navigate(
      `/workflow-builder/${policy.id}`,
    );
  };

  const handleSave = () => {
    setFormError("");

    try {
      const condition =
        JSON.parse(form.condition) as Record<
          string,
          unknown
        >;

      const action =
        JSON.parse(form.action) as Record<
          string,
          unknown
        >;

      if (!form.name.trim()) {
        setFormError(
          "Policy name is required.",
        );
        return;
      }

      if (editingId === null) {
        createMutation.mutate({
          name: form.name.trim(),
          description:
            form.description.trim() ||
            undefined,
          enabled: form.enabled,
          condition,
          action,
        });

        return;
      }

      updateMutation.mutate({
        id: editingId,
        policy: {
          name: form.name.trim(),
          description:
            form.description.trim(),
          enabled: form.enabled,
          condition,
          action,
        },
      });
    } catch {
      setFormError(
        "Condition and Action must contain valid JSON.",
      );
    }
  };

  const togglePolicy = (
    policy: (typeof policies)[number],
  ) => {
    updateMutation.mutate({
      id: policy.id,
      policy: {
        enabled: !policy.enabled,
      },
    });
  };

  if (isLoading) {
    return (
      <Typography>
        Loading notification workflows...
      </Typography>
    );
  }

  if (isError) {
    return (
      <MuiAlert severity="error">
        Unable to load notification workflows.
      </MuiAlert>
    );
  }

  const saving =
    createMutation.isPending ||
    updateMutation.isPending;

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
            Notification Workflows
          </Typography>

          <Typography color="text.secondary">
            Create and manage notification
            policies for automated incident
            response.
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
            to="/workflow-builder"
            variant="outlined"
          >
            Notification Workflow Builder
          </Button>

          {/* <Button
            component={RouterLink}
            to="/correlation-workflows"
            variant="outlined"
          >
            Correlation Workflows
          </Button> */}

          <Button
            variant="contained"
            onClick={openCreate}
          >
            Create Policy
          </Button>
        </Stack>
      </Stack>

      {createMutation.isError && (
        <MuiAlert
          severity="error"
          sx={{ mb: 2 }}
        >
          Failed to create notification policy.
        </MuiAlert>
      )}

      {updateMutation.isError && (
        <MuiAlert
          severity="error"
          sx={{ mb: 2 }}
        >
          Failed to update notification policy.
        </MuiAlert>
      )}

      <TableContainer
        component={Paper}
        elevation={2}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Policy</TableCell>
              <TableCell>Condition</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Status</TableCell>
              <TableCell />
            </TableRow>
          </TableHead>

          <TableBody>
            {policies.map((policy) => (
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
                    {policy.description ??
                      "No description"}
                  </Typography>
                </TableCell>

                <TableCell>
                  <Typography
                    variant="body2"
                    sx={{
                      whiteSpace:
                        "pre-wrap",
                    }}
                  >
                    {JSON.stringify(
                      policy.condition,
                    )}
                  </Typography>
                </TableCell>

                <TableCell>
                  <Typography
                    variant="body2"
                  >
                    {String(
                      policy.action?.type ??
                        "Unknown",
                    )}
                  </Typography>
                </TableCell>

                <TableCell>
                  <Chip
                    label={
                      policy.enabled
                        ? "Enabled"
                        : "Disabled"
                    }
                    size="small"
                    color={
                      policy.enabled
                        ? "success"
                        : "default"
                    }
                  />
                </TableCell>

                <TableCell>
                  <Stack
                    direction="row"
                    spacing={1}
                  >
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() =>
                        openEdit(policy)
                      }
                    >
                      Edit
                    </Button>

                    <Button
                      size="small"
                      onClick={() =>
                        togglePolicy(policy)
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
            ))}

            {policies.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={6}
                  align="center"
                >
                  No notification workflows
                  found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={dialogOpen}
        onClose={closeDialog}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          {editingId === null
            ? "Create Notification Policy"
            : "Edit Notification Policy"}
        </DialogTitle>

        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              fullWidth
              label="Policy Name"
              value={form.name}
              onChange={(event) =>
                setForm({
                  ...form,
                  name: event.target.value,
                })
              }
            />

            <TextField
              fullWidth
              label="Description"
              value={form.description}
              onChange={(event) =>
                setForm({
                  ...form,
                  description:
                    event.target.value,
                })
              }
            />

            <TextField
              fullWidth
              multiline
              minRows={10}
              label="Condition JSON"
              value={form.condition}
              onChange={(event) =>
                setForm({
                  ...form,
                  condition:
                    event.target.value,
                })
              }
              inputProps={{
                style: {
                  fontFamily:
                    "monospace",
                },
              }}
            />

            <TextField
              fullWidth
              multiline
              minRows={10}
              label="Action JSON"
              value={form.action}
              onChange={(event) =>
                setForm({
                  ...form,
                  action:
                    event.target.value,
                })
              }
              inputProps={{
                style: {
                  fontFamily:
                    "monospace",
                },
              }}
            />

            {formError && (
              <MuiAlert severity="error">
                {formError}
              </MuiAlert>
            )}
          </Stack>
        </DialogContent>

        <DialogActions>
          <Button onClick={closeDialog}>
            Cancel
          </Button>

          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving}
          >
            {saving
              ? "Saving..."
              : editingId === null
                ? "Create Policy"
                : "Update Policy"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}