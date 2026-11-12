import {
  AuthResponse,
  DocumentListItem,
  Job,
  DocumentAnalysis,
  User,
  TelemetryEvent,
} from "../types";

const API_BASE = "";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem("auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Login failed" }));
    throw new ApiError(res.status, err.detail || "Authentication failed");
  }
  const data = await res.json();
  localStorage.setItem("auth_token", data.access_token);
  return data;
}

export async function registerUser(email: string, password: string, full_name: string): Promise<User> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Registration failed" }));
    throw new ApiError(res.status, err.detail || "Registration failed");
  }
  return res.json();
}

export async function getCurrentUser(): Promise<User> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { ...getAuthHeader() },
  });
  if (!res.ok) {
    throw new ApiError(res.status, "Unauthorized");
  }
  return res.json();
}

export async function uploadDocument(file: File, referenceId?: string): Promise<{
  document_id: string;
  job_id: string;
  filename: string;
  status: string;
  is_duplicate: boolean;
  message: string;
}> {
  const formData = new FormData();
  formData.append("file", file);
  if (referenceId) {
    formData.append("reference_id", referenceId);
  }

  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: "POST",
    headers: { ...getAuthHeader() },
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new ApiError(res.status, err.detail || "Failed to upload document");
  }
  return res.json();
}

export async function listDocuments(): Promise<DocumentListItem[]> {
  const res = await fetch(`${API_BASE}/api/documents/`, {
    headers: { ...getAuthHeader() },
  });
  if (!res.ok) {
    throw new ApiError(res.status, "Failed to load documents");
  }
  return res.json();
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
    headers: { ...getAuthHeader() },
  });
  if (!res.ok) {
    throw new ApiError(res.status, "Failed to load job details");
  }
  return res.json();
}

export async function getDocumentAnalysis(documentId: string): Promise<DocumentAnalysis> {
  const res = await fetch(`${API_BASE}/api/analysis/${documentId}`, {
    headers: { ...getAuthHeader() },
  });
  if (!res.ok) {
    throw new ApiError(res.status, "Failed to load document analysis");
  }
  return res.json();
}

export function subscribeToJobEvents(
  jobId: string,
  onEvent: (event: TelemetryEvent) => void,
  onError?: (err: any) => void
): () => void {
  const token = localStorage.getItem("auth_token");
  const eventSource = new EventSource(`${API_BASE}/api/jobs/${jobId}/events`);

  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onEvent(data);
    } catch (err) {
      console.error("Error parsing SSE event:", err);
    }
  };

  eventSource.onerror = (e) => {
    if (onError) onError(e);
  };

  return () => {
    eventSource.close();
  };
}
