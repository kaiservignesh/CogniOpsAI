import apiClient from "./client";

export interface Situation {
  id: number;
  title: string;
  description?: string | null;
  severity: string;
  status: string;
  service?: string | null;
  environment?: string | null;
  created_at: string;
  updated_at: string;
  alert_count: number;

  correlation_score?: number | null;
  correlation_method?: string | null;
  correlation_reasons?: string[] | null;

  ai_summary?: string | null;
  ai_root_cause?: string | null;
  ai_recommendations?: string | null;
  ai_status: string;
  ai_updated_at?: string | null;
}

export async function getSituations(): Promise<Situation[]> {
  const response = await apiClient.get<Situation[]>(
    "/situations/",
  );

  return response.data;
}