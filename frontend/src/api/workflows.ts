import apiClient from "./client";

export interface WorkflowExecution {
  id: number;
  situation_id: number;
  policy_id: number;
  status: string;
  action_type?: string | null;
  action_target?: string | null;
  action_payload?: Record<string, unknown> | null;
  result?: string | null;
  created_at: string;
  updated_at: string;
}

export async function getWorkflowExecutions(): Promise<
  WorkflowExecution[]
> {
  const response = await apiClient.get<
    WorkflowExecution[]
  >("/workflows/policies/executions/");

  return response.data;
}