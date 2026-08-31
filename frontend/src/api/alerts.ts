import apiClient from "./client";

export interface Alert {
  id: number;
  title: string;
  description?: string | null;
  source: string;
  severity: string;
  status: string;
  policy_name?: string | null;
  tags?: string | null;
  service?: string | null;
  environment?: string | null;
  situation_id?: number | null;
  created_at: string;
  updated_at: string;
}

export async function getAlerts(): Promise<Alert[]> {
  const response = await apiClient.get<Alert[]>("/alerts/");
  return response.data;
}