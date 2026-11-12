import React, { useState, useEffect } from "react";
import {
  Upload,
  FileText,
  Clock,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  FolderOpen,
} from "lucide-react";
import { DocumentListItem, User } from "../types";
import { listDocuments } from "../api/client";
import { UploadModal } from "../components/UploadModal";

interface DashboardPageProps {
  currentUser: User;
  onOpenDocument: (documentId: string, jobId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  currentUser,
  onOpenDocument,
}) => {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);

  const loadDocs = async () => {
    setIsLoading(true);
    try {
      const data = await listDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleUploadSuccess = (jobId: string, documentId: string) => {
    onOpenDocument(documentId, jobId);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-slate-200 gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Clinical Verification Workbench</h1>
          <p className="text-xs text-slate-500 mt-1">
            Audit prescribed inpatient discharge regimens against institutional formulary monographs
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadDocs}
            className="p-2 border border-slate-200 text-slate-600 hover:bg-slate-50 rounded-lg text-xs font-medium transition"
            title="Refresh documents list"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-lg text-xs font-semibold shadow-xs flex items-center space-x-2 transition"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Discharge Summary</span>
          </button>
        </div>
      </div>

      {/* Overview Metric Pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6">
        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Ingested Documents</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{documents.length}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Discharge summaries evaluated</div>
        </div>

        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Target Formulary</div>
          <div className="text-sm font-bold text-sky-800 mt-2 truncate">Meridian Bay Digest Rev 8.2</div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-0.5">8 Monograph Categories Active</div>
        </div>

        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Grounding Standard</div>
          <div className="text-sm font-bold text-slate-900 mt-2">Zero-Hallucination RAG</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Parameter Concordance + Citations</div>
        </div>
      </div>

      {/* Documents Table / List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FolderOpen className="w-4 h-4 text-slate-500" />
            <h2 className="font-semibold text-xs text-slate-800 uppercase tracking-wider">
              Recent Verification Audits
            </h2>
          </div>
          <span className="text-[11px] text-slate-400">{documents.length} entries</span>
        </div>

        {isLoading ? (
          <div className="p-12 text-center text-slate-400">
            <div className="w-6 h-6 border-2 border-sky-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <p className="text-xs">Loading clinical records...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <h3 className="font-semibold text-sm text-slate-800 mb-1">No discharge summaries uploaded yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mb-4">
              Upload the sample primary discharge summary (`primary_document_medical.docx`) to run the asynchronous verification pipeline.
            </p>
            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="px-4 py-2 bg-sky-600 text-white rounded-lg text-xs font-semibold hover:bg-sky-700 transition"
            >
              Upload Document
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 text-xs">
            {documents.map((doc) => (
              <div
                key={doc.id}
                onClick={() => onOpenDocument(doc.id, doc.latest_job_id)}
                className="p-4 flex items-center justify-between hover:bg-sky-50/40 cursor-pointer transition"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-sky-50 text-sky-700">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-bold text-slate-900">{doc.filename}</div>
                    <div className="text-[11px] text-slate-500 flex items-center space-x-2 mt-0.5">
                      <span className="uppercase font-mono font-semibold">{doc.file_type}</span>
                      <span>•</span>
                      <span>{new Date(doc.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  {doc.latest_job_status === "completed" && (
                    <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Audit Complete</span>
                    </span>
                  )}
                  {doc.latest_job_status === "processing" && (
                    <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-sky-100 text-sky-800">
                      <Clock className="w-3.5 h-3.5 animate-spin" />
                      <span>Processing...</span>
                    </span>
                  )}
                  {doc.latest_job_status === "failed" && (
                    <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-rose-100 text-rose-800">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>Audit Error</span>
                    </span>
                  )}

                  <ArrowRight className="w-4 h-4 text-slate-400" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
};
