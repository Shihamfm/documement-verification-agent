import React from "react";
import { CheckCircle2, Circle, Loader2, AlertCircle, Clock } from "lucide-react";
import { Job, JobStage } from "../types";

interface PipelineTrackerProps {
  job: Job | null;
  currentStage: string;
  progressPercentage: number;
  stagesTelemetry: Array<{ stage_name: string; status: string; duration_seconds: number }>;
  errorMessage?: string;
}

const STAGE_CONFIG: Record<string, { label: string; desc: string }> = {
  parsed: { label: "Parse Document", desc: "Extracting text, patient info, and clinical sections" },
  chunked: { label: "Monograph Chunker", desc: "Partitioning formulary into discrete monograph units" },
  embedded: { label: "Vector Embeddings", desc: "Computing semantic embeddings with pgvector" },
  summarized: { label: "Discharge Summary", desc: "Synthesizing clinical overview & hospital course" },
  key_points_extracted: { label: "Critical Points", desc: "Surfacing patient safety warnings & lab schedules" },
  entities_extracted: { label: "Rx Extraction", desc: "Extracting structured medication parameters" },
  verified: { label: "Formulary Verification", desc: "Targeted RAG retrieval & parameter concordance" },
  done: { label: "Verification Complete", desc: "All stages finalized and grounded citations verified" },
};

export const PipelineTracker: React.FC<PipelineTrackerProps> = ({
  job,
  currentStage,
  progressPercentage,
  stagesTelemetry,
  errorMessage,
}) => {
  const stageKeys = [
    "parsed",
    "chunked",
    "embedded",
    "summarized",
    "key_points_extracted",
    "entities_extracted",
    "verified",
  ];

  // Helper to determine stage state
  const getStageStatus = (stageKey: string): "completed" | "in_progress" | "pending" | "failed" => {
    if (job?.status === "failed" && currentStage === stageKey) return "failed";
    const found = stagesTelemetry.find((s) => s.stage_name === stageKey);
    if (found) {
      if (found.status === "completed") return "completed";
      if (found.status === "in_progress") return "in_progress";
      if (found.status === "failed") return "failed";
    }
    if (job?.status === "completed") return "completed";
    return "pending";
  };

  const getStageDuration = (stageKey: string): string => {
    const found = stagesTelemetry.find((s) => s.stage_name === stageKey);
    return found && found.duration_seconds > 0 ? `${found.duration_seconds.toFixed(2)}s` : "";
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-100 mb-6">
        <div>
          <h2 className="text-base font-semibold text-slate-900 flex items-center space-x-2">
            <span>Asynchronous Verification Pipeline</span>
            {job?.status === "processing" && (
              <span className="flex items-center space-x-1 text-xs text-sky-600 bg-sky-50 px-2.5 py-0.5 rounded-full font-medium">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Live Telemetry</span>
              </span>
            )}
            {job?.status === "completed" && (
              <span className="flex items-center space-x-1 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Pipeline Complete</span>
              </span>
            )}
            {job?.status === "failed" && (
              <span className="flex items-center space-x-1 text-xs text-rose-700 bg-rose-50 px-2.5 py-0.5 rounded-full font-medium">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Stage Error</span>
              </span>
            )}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time stage transitions streamed via Server-Sent Events (SSE). Reconnection and refresh persistent.
          </p>
        </div>

        {/* Progress % */}
        <div className="mt-3 sm:mt-0 flex items-center space-x-3">
          <div className="text-right">
            <span className="text-sm font-bold text-slate-800">{progressPercentage}%</span>
            <div className="text-[10px] text-slate-400">Completion</div>
          </div>
          <div className="w-24 sm:w-32 bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                job?.status === "failed" ? "bg-rose-500" : "bg-sky-600"
              }`}
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Granular Pipeline Stepper */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-7 gap-3">
        {stageKeys.map((stageKey, idx) => {
          const status = getStageStatus(stageKey);
          const config = STAGE_CONFIG[stageKey] || { label: stageKey, desc: "" };
          const duration = getStageDuration(stageKey);

          return (
            <div
              key={stageKey}
              className={`flex flex-col justify-between p-3 rounded-lg border text-xs transition-all ${
                status === "completed"
                  ? "bg-emerald-50/50 border-emerald-200 text-slate-800"
                  : status === "in_progress"
                  ? "bg-sky-50 border-sky-300 text-sky-900 shadow-sm ring-1 ring-sky-200"
                  : status === "failed"
                  ? "bg-rose-50 border-rose-300 text-rose-900"
                  : "bg-slate-50/60 border-slate-200 text-slate-400"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono text-[10px] font-bold text-slate-400">
                    0{idx + 1}
                  </span>
                  <div>
                    {status === "completed" && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    )}
                    {status === "in_progress" && (
                      <Loader2 className="w-4 h-4 text-sky-600 animate-spin" />
                    )}
                    {status === "failed" && (
                      <AlertCircle className="w-4 h-4 text-rose-600" />
                    )}
                    {status === "pending" && (
                      <Circle className="w-4 h-4 text-slate-300" />
                    )}
                  </div>
                </div>

                <div className="font-semibold leading-tight text-slate-900 mb-0.5">
                  {config.label}
                </div>
                <div className="text-[10px] text-slate-500 line-clamp-2 leading-relaxed">
                  {config.desc}
                </div>
              </div>

              {duration && (
                <div className="mt-2 pt-1.5 border-t border-slate-100 flex items-center text-[10px] text-slate-500 font-mono">
                  <Clock className="w-3 h-3 mr-1 text-slate-400" />
                  <span>{duration}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 mt-0.5 text-rose-600 flex-shrink-0" />
          <div>
            <span className="font-semibold">Pipeline Failure: </span>
            <span>{errorMessage}</span>
          </div>
        </div>
      )}
    </div>
  );
};
