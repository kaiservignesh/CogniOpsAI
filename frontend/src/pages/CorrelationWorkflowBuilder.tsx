import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Link as RouterLink,
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  addEdge,
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { useAppTheme } from "../theme/useAppTheme";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";

import {
  createCorrelationPolicy,
  getCorrelationPolicy,
  updateCorrelationPolicy,
  type CorrelationRule,
} from "../api/correlationPolicies";

interface RuleRow
  extends CorrelationRule {
  id: number;
}

const fields = [
  {
    value: "source",
    label: "Source",
  },
  {
    value: "policy_name",
    label: "Policy Name",
  },
  {
    value: "service",
    label: "Service",
  },
  {
    value: "environment",
    label: "Environment",
  },
  {
    value: "severity",
    label: "Severity",
  },
  {
    value: "tag",
    label: "Tag",
  },
  {
    value: "title",
    label: "Alert Title",
  },
];

const initialNodes: Node[] = [
  {
    id: "policy",
    position: {
      x: 40,
      y: 150,
    },
    data: {
      label: "Correlation Policy",
    },
    type: "policy",
  },
  {
    id: "rules",
    position: {
      x: 300,
      y: 150,
    },
    data: {
      label: "Matching Rules",
    },
    type: "rules",
  },
  {
    id: "window",
    position: {
      x: 560,
      y: 150,
    },
    data: {
      label: "Time Window",
    },
    type: "window",
  },
  {
    id: "correlate",
    position: {
      x: 820,
      y: 150,
    },
    data: {
      label: "Correlate Alerts",
    },
    type: "correlate",
  },
];

const initialEdges: Edge[] = [
  {
    id: "policy-rules",
    source: "policy",
    target: "rules",
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: "rules-window",
    source: "rules",
    target: "window",
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: "window-correlate",
    source: "window",
    target: "correlate",
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
];

function FlowNode({
  data,
}: {
  data: {
    label: string;
  };
}) {
  return (
    <Box
      sx={{
        minWidth: 180,
        border: 2,
        borderColor: "primary.main",
        borderRadius: 2,
        bgcolor:
          "background.paper",
        p: 2,
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
      />

      <Typography fontWeight={700}>
        {data.label}
      </Typography>

      <Handle
        type="source"
        position={Position.Right}
      />
    </Box>
  );
}

const nodeTypes = {
  policy: FlowNode,
  rules: FlowNode,
  window: FlowNode,
  correlate: FlowNode,
};

export default function CorrelationWorkflowBuilder() {
  const { mode: themeMode } = useAppTheme();
  const navigate = useNavigate();

  const { id } =
    useParams<{
      id?: string;
    }>();

  const editingId = id
    ? Number(id)
    : null;

  const [
    nodes,
    ,
    onNodesChange,
  ] = useNodesState(
    initialNodes,
  );

  const [
    edges,
    setEdges,
    onEdgesChange,
  ] = useEdgesState(
    initialEdges,
  );

  const [name, setName] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [
    matchMode,
    setMatchMode,
  ] = useState<
    "all" | "any"
  >("all");

  const [
    timeWindow,
    setTimeWindow,
  ] = useState(5);

  const [rules, setRules] =
    useState<RuleRow[]>([
      {
        id: 1,
        field: "source",
        operator: "equals",
        value: "Grafana",
      },
    ]);

  const [saving, setSaving] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [mode, setMode] =
    useState<
      "visual" | "json"
    >("visual");

  const [jsonText, setJsonText] =
    useState("");

  const [
    loadingPolicy,
    setLoadingPolicy,
  ] = useState(
    Boolean(editingId),
  );

  /*
   * IMPORTANT:
   * activeRules MUST be defined before
   * the useEffect that references it.
   */
  const activeRules =
    useMemo(
      () =>
        rules.filter(
          (rule) =>
            rule.value.trim(),
        ),
      [rules],
    );

  useEffect(() => {
    if (!editingId) {
      //setJsonText("");
      //setLoadingPolicy(false);
      return;
    }

    getCorrelationPolicy(
      editingId,
    )
      .then((policy) => {
        setName(policy.name);

        setDescription(
          policy.description ??
            "",
        );

        setMatchMode(
          policy.condition
            ?.match ?? "all",
        );

        setTimeWindow(
          Math.max(
            1,
            Number(
              policy.time_window_minutes,
            ) || 1,
          ),
        );

        setRules(
          (
            policy.condition
              ?.rules ?? []
          ).map(
            (
              rule,
              index,
            ) => ({
              ...rule,
              id: index + 1,
            }),
          ),
        );

        setJsonText(
          JSON.stringify(
            {
              name: policy.name,
              description:
                policy.description ??
                "",
              enabled:
                policy.enabled,
              condition:
                policy.condition,
              time_window_minutes:
                policy.time_window_minutes,
            },
            null,
            2,
          ),
        );
      })
      .catch(() => {
        setMessage(
          "Unable to load correlation workflow.",
        );
      })
      .finally(() => {
        setLoadingPolicy(false);
      });
  }, [editingId]);

  const generatedJson = useMemo(
    () =>
      JSON.stringify(
        {
          name: name.trim(),
          description:
            description.trim() ||
            undefined,
          enabled: true,
          condition: {
            match: matchMode,
            rules: activeRules.map(
              (rule) => ({
                field: rule.field,
                operator: rule.operator,
                value: rule.value,
              }),
            ),
          },
          time_window_minutes:
            timeWindow,
        },
        null,
        2,
      ),
    [
      name,
      description,
      matchMode,
      timeWindow,
      activeRules,
    ],
  );

  const previewJson =
    mode === "json" ? jsonText : generatedJson;

  const onConnect =
    useCallback(
      (
        connection: Connection,
      ) => {
        setEdges(
          (current) =>
            addEdge(
              {
                ...connection,
                markerEnd: {
                  type: MarkerType.ArrowClosed,
                },
              },
              current,
            ),
        );
      },
      [setEdges],
    );

  const updateRule = (
    ruleId: number,
    patch: Partial<RuleRow>,
  ) => {
    setRules(
      (current) =>
        current.map(
          (rule) =>
            rule.id === ruleId
              ? {
                  ...rule,
                  ...patch,
                }
              : rule,
        ),
    );
  };

  const addRule = () => {
    setRules(
      (current) => [
        ...current,
        {
          id: Date.now(),
          field: "service",
          operator: "equals",
          value: "",
        },
      ],
    );
  };

  const removeRule = (
    ruleId: number,
  ) => {
    setRules(
      (current) =>
        current.filter(
          (rule) =>
            rule.id !== ruleId,
        ),
    );
  };

  const handleJsonToVisual =
    () => {
      try {
        const parsed =
          JSON.parse(jsonText);

        if (
          !parsed.name?.trim()
        ) {
          setMessage(
            "Policy name is required.",
          );
          return false;
        }

        const parsedRules =
          parsed.condition
            ?.rules ?? [];

        if (
          !Array.isArray(
            parsedRules,
          )
        ) {
          setMessage(
            "condition.rules must be an array.",
          );
          return false;
        }

        setName(
          parsed.name,
        );

        setDescription(
          parsed.description ??
            "",
        );

        setMatchMode(
          parsed.condition
            ?.match ?? "all",
        );

        setTimeWindow(
          Math.max(
            1,
            Number(
              parsed.time_window_minutes,
            ) || 1,
          ),
        );

        setRules(
          parsedRules.map(
            (
              rule: CorrelationRule,
              index: number,
            ) => ({
              ...rule,
              id: index + 1,
            }),
          ),
        );

        return true;
      } catch {
        setMessage(
          "JSON is invalid. Fix it before switching to Visual Builder.",
        );
        return false;
      }
    };

  const handleSave =
    async () => {
      setMessage("");

      try {
        const parsed =
          JSON.parse(
            jsonText,
          ) as {
            name: string;
            description?: string;
            enabled?: boolean;
            condition: {
              match:
                | "all"
                | "any";
              rules: CorrelationRule[];
            };
            time_window_minutes: number;
          };

        if (
          !parsed.name?.trim()
        ) {
          setMessage(
            "Correlation policy name is required.",
          );
          return;
        }

        if (
          !parsed.condition
            ?.rules?.length
        ) {
          setMessage(
            "Add at least one correlation rule.",
          );
          return;
        }

        const payload = {
          name:
            parsed.name.trim(),

          description:
            parsed.description
              ?.trim() ||
            undefined,

          enabled:
            parsed.enabled ??
            true,

          condition:
            parsed.condition,

          time_window_minutes:
            Math.max(
              1,
              Number(
                parsed.time_window_minutes,
              ) || 1,
            ),
        };

        setSaving(true);

        if (editingId) {
          await updateCorrelationPolicy(
            editingId,
            payload,
          );
        } else {
          await createCorrelationPolicy(
            payload,
          );
        }

        navigate(
          "/correlation-workflows",
        );
      } catch {
        setMessage(
          "The JSON is invalid. Please correct it before saving.",
        );
      } finally {
        setSaving(false);
      }
    };

  if (loadingPolicy) {
    return (
      <Typography>
        Loading correlation workflow...
      </Typography>
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
            {editingId
              ? "Edit Correlation Workflow"
              : "Correlation Workflow Builder"}
          </Typography>

          <Typography color="text.secondary">
            Define which alert attributes must
            match before alerts are grouped into
            the same Situation.
          </Typography>
        </Box>

        <Button
          component={RouterLink}
          to="/correlation-workflows"
          variant="outlined"
        >
          View Correlation Workflows
        </Button>
      </Stack>

      <Tabs
        value={mode}
        onChange={(_, value) => {
          if (
            value === "visual" &&
            mode === "json"
          ) {
            if (!handleJsonToVisual()) {
              return;
            }
          }

          if (
            value === "json" &&
            mode === "visual"
          ) {
            setJsonText(generatedJson);
          }

          setMode(value);
        }}
        sx={{ mb: 2 }}
      >
        <Tab
          value="visual"
          label="Visual Builder"
        />

        <Tab
          value="json"
          label="JSON"
        />
      </Tabs>

      {mode === "json" && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography
              variant="h6"
              fontWeight={700}
              gutterBottom
            >
              Generated / Editable JSON
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 2 }}
            >
              Edit the same correlation policy
              JSON used by the backend.
            </Typography>

            <TextField
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
          </CardContent>
        </Card>
      )}

      {mode === "visual" && (
        <Stack spacing={3}>
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <TextField
                  fullWidth
                  label="Policy Name"
                  value={name}
                  onChange={(
                    event,
                  ) =>
                    setName(
                      event.target
                        .value,
                    )
                  }
                />

                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  value={
                    description
                  }
                  onChange={(
                    event,
                  ) =>
                    setDescription(
                      event.target
                        .value,
                    )
                  }
                />

                <Stack
                  direction={{
                    xs: "column",
                    md: "row",
                  }}
                  spacing={2}
                >
                  <FormControl
                    fullWidth
                  >
                    <InputLabel>
                      Rule Matching
                    </InputLabel>

                    <Select
                      value={
                        matchMode
                      }
                      label="Rule Matching"
                      onChange={(
                        event,
                      ) =>
                        setMatchMode(
                          event.target
                            .value as
                            | "all"
                            | "any",
                        )
                      }
                    >
                      <MenuItem value="all">
                        All rules must match
                      </MenuItem>

                      <MenuItem value="any">
                        Any rule can match
                      </MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    fullWidth
                    label="Time Window (minutes)"
                    type="number"
                    value={
                      timeWindow
                    }
                    onChange={(
                      event,
                    ) =>
                      setTimeWindow(
                        Math.max(
                          1,
                          Number(
                            event.target
                              .value,
                          ) || 1,
                        ),
                      )
                    }
                  />
                </Stack>
              </Stack>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Stack spacing={2}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Box>
                    <Typography
                      variant="h6"
                      fontWeight={700}
                    >
                      Matching Rules
                    </Typography>

                    <Typography
                      variant="body2"
                      color="text.secondary"
                    >
                      Define which alert attributes
                      should match.
                    </Typography>
                  </Box>

                  <Button
                    variant="outlined"
                    onClick={
                      addRule
                    }
                  >
                    Add Rule
                  </Button>
                </Stack>

                {rules.map(
                  (rule) => (
                    <Stack
                      key={
                        rule.id
                      }
                      direction={{
                        xs: "column",
                        md: "row",
                      }}
                      spacing={2}
                    >
                      <FormControl
                        fullWidth
                      >
                        <InputLabel>
                          Field
                        </InputLabel>

                        <Select
                          value={
                            rule.field
                          }
                          label="Field"
                          onChange={(
                            event,
                          ) =>
                            updateRule(
                              rule.id,
                              {
                                field:
                                  event
                                    .target
                                    .value,
                              },
                            )
                          }
                        >
                          {fields.map(
                            (
                              field,
                            ) => (
                              <MenuItem
                                key={
                                  field.value
                                }
                                value={
                                  field.value
                                }
                              >
                                {
                                  field.label
                                }
                              </MenuItem>
                            ),
                          )}
                        </Select>
                      </FormControl>

                      <FormControl
                        fullWidth
                      >
                        <InputLabel>
                          Operator
                        </InputLabel>

                        <Select
                          value={
                            rule.operator
                          }
                          label="Operator"
                          onChange={(
                            event,
                          ) =>
                            updateRule(
                              rule.id,
                              {
                                operator:
                                  event
                                    .target
                                    .value,
                              },
                            )
                          }
                        >
                          <MenuItem value="equals">
                            Equals
                          </MenuItem>

                          <MenuItem value="contains">
                            Contains
                          </MenuItem>

                          <MenuItem value="not_equals">
                            Not equals
                          </MenuItem>
                        </Select>
                      </FormControl>

                      <TextField
                        fullWidth
                        label="Value"
                        value={
                          rule.value
                        }
                        onChange={(
                          event,
                        ) =>
                          updateRule(
                            rule.id,
                            {
                              value:
                                event
                                  .target
                                  .value,
                            },
                          )
                        }
                      />

                      <IconButton
                        color="error"
                        onClick={() =>
                          removeRule(
                            rule.id,
                          )
                        }
                        disabled={
                          rules.length ===
                          1
                        }
                      >
                        ×
                      </IconButton>
                    </Stack>
                  ),
                )}
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
                Visual Flow
              </Typography>

              <Box
                sx={{
                  height: 360,
                  border: 1,
                  borderColor:
                    "divider",
                  borderRadius: 2,
                }}
              >
                <ReactFlow
                  className={themeMode === "dark" ? "dark" : ""}
                  nodes={nodes}
                  edges={edges}
                  nodeTypes={
                    nodeTypes
                  }
                  onNodesChange={
                    onNodesChange
                  }
                  onEdgesChange={
                    onEdgesChange
                  }
                  onConnect={
                    onConnect
                  }
                  fitView
                >
                  <Background />
                  <Controls />
                  <MiniMap />
                </ReactFlow>
              </Box>
            </CardContent>
          </Card>
        </Stack>
      )}

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
            sx={{ mb: 2 }}
          >
            <Box>
              <Typography
                variant="h6"
                fontWeight={700}
              >
                JSON Preview
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                Generated automatically from the visual workflow.
              </Typography>
            </Box>

            <Button
              variant="outlined"
              onClick={() =>
                navigator.clipboard.writeText(previewJson)
              }
            >
              Copy JSON
            </Button>
          </Stack>

          <TextField
            fullWidth
            multiline
            minRows={12}
            value={previewJson}
            InputProps={{
              readOnly: true,
            }}
            inputProps={{
              style: {
                fontFamily: "monospace",
                fontSize: "13px",
              },
            }}
          />
        </CardContent>
      </Card>

      <Alert
        severity="info"
        sx={{ mt: 3 }}
      >
        User-defined correlation policies
        work together with the existing
        score-based correlation engine.
      </Alert>

      <Stack
        direction="row"
        justifyContent="flex-end"
        sx={{ mt: 3 }}
      >
        <Button
          variant="contained"
          size="large"
          onClick={handleSave}
          disabled={saving}
        >
          {saving
            ? "Saving..."
            : editingId
              ? "Update Correlation Workflow"
              : "Save Correlation Workflow"}
        </Button>
      </Stack>

      <Snackbar
        open={Boolean(message)}
        autoHideDuration={4000}
        onClose={() =>
          setMessage("")
        }
      >
        <Alert
          severity="error"
          onClose={() =>
            setMessage("")
          }
        >
          {message}
        </Alert>
      </Snackbar>
    </Box>
  );
}