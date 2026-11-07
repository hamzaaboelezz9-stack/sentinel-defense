export type Row = Record<string, any>;
export interface SecurityEvent {
  id: string;
  timestamp: string;
  device_id: string;
  source_ip: string;
  destination_ip?: string | null;
  username: string;
  category: "authentication" | "network" | "device";
  event_type: "login" | "access_denied" | "configuration_change" | "telemetry";
  status: "success" | "failure";
  severity: "low" | "medium" | "high" | "critical";
  environment: "synthetic-lab";
  disabled_account: boolean;
  telemetry: number;
  label?: 0 | 1 | null;
  related_incident_id?: string | null;
}
export interface Incident {
  id: string;
  rule: string;
  rule_version: string;
  severity: string;
  timestamp: string;
  device_id: string;
  explanation: string;
  evidence: string[];
  status: string;
  assignment: string;
  history: Row[];
}
