export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  full_name: string;
}

export interface DocumentListItem {
  id: string;
  filename: string;
  file_type: string;
  document_type: string;
  created_at: string;
  latest_job_id?: string;
  latest_job_status?: string;
}

export interface JobStage {
  id: string;
  stage_name: string;
  order: number;
  status: "pending" | "in_progress" | "completed" | "failed";
  duration_seconds: number;
  stage_metadata: Record<string, any>;
  started_at?: string;
  completed_at?: string;
}

export interface Job {
  id: string;
  user_id: string;
  primary_document_id: string;
  reference_document_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  current_stage: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  stages: JobStage[];
}

export interface TelemetryEvent {
  job_id: string;
  stage_name: string;
  status: string;
  progress_percentage: number;
  metadata?: Record<string, any>;
  error_message?: string;
  timestamp: string;
  stages?: Array<{ stage_name: string; status: string; duration_seconds: number }>;
}

export interface VerificationResult {
  id: string;
  status: "Supported" | "Contradicted" | "Unsupported";
  explanation: string;
  parameter_matches: {
    dose_matched?: boolean;
    frequency_matched?: boolean;
    duration_matched?: boolean;
    timing_matched?: boolean;
    indication_matched?: boolean;
    in_formulary?: boolean;
    details?: Record<string, any>;
  };
  citation_section?: string;
  citation_monograph?: string;
  citation_passage?: string;
  created_at: string;
}

export interface PrescribedEntity {
  id: string;
  medication_name: string;
  dose: string;
  unit: string;
  route: string;
  frequency: string;
  duration: string;
  indication: string;
  source_section: string;
  raw_attributes: Record<string, any>;
  verification?: VerificationResult;
}

export interface CriticalPoint {
  id: string;
  point_text: string;
  category: string;
  severity: "High" | "Medium" | "Low";
  source_quote: string;
  rank_order: number;
}

export interface DocumentSummary {
  id: string;
  executive_summary: string;
  clinical_highlights: {
    admission_reason?: string;
    diagnoses?: string[];
    stabilization_status?: string;
    care_team?: string;
  };
  created_at: string;
}

export interface DocumentAnalysis {
  document_id: string;
  filename: string;
  patient_info: {
    patient_name?: string;
    age?: number;
    gender?: string;
    mrn?: string;
    admission_date?: string;
    discharge_date?: string;
    attending?: string;
    service?: string;
  };
  summary?: DocumentSummary;
  critical_points: CriticalPoint[];
  prescribed_entities: PrescribedEntity[];
  raw_text: string;
  sections: Record<string, string>;
  total_medications: number;
  supported_count: number;
  contradicted_count: number;
  unsupported_count: number;
}
