import React from "react";
import { Sparkles, FileText, CheckCircle, Activity, Stethoscope } from "lucide-react";
import { DocumentSummary } from "../types";

interface SummaryViewProps {
  summary?: DocumentSummary;
}

export const SummaryView: React.FC<SummaryViewProps> = ({ summary }) => {
  if (!summary) {
    return (
      <div className="p-8 text-center text-slate-400">
        <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-xs">Summary generation in progress or unavailable.</p>
      </div>
    );
  }

  const h = summary.clinical_highlights || {};

  return (
    <div className="space-y-4">
      {/* Executive Summary Narrative */}
      <div className="bg-sky-50/50 border border-sky-100 rounded-xl p-5">
        <div className="flex items-center space-x-2 text-sky-800 text-xs font-semibold mb-2">
          <Sparkles className="w-4 h-4 text-sky-600" />
          <span>LLM Executive Clinical Synthesis</span>
        </div>
        <p className="text-slate-800 text-xs leading-relaxed whitespace-pre-line font-normal">
          {summary.executive_summary}
        </p>
      </div>

      {/* Clinical Highlights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        {h.admission_reason && (
          <div className="p-3 bg-white border border-slate-200 rounded-lg">
            <div className="text-[10px] uppercase font-bold text-slate-400 mb-1 flex items-center space-x-1">
              <Activity className="w-3.5 h-3.5 text-rose-500" />
              <span>Admission Trigger</span>
            </div>
            <p className="text-slate-800 font-medium">{h.admission_reason}</p>
          </div>
        )}

        {h.stabilization_status && (
          <div className="p-3 bg-white border border-slate-200 rounded-lg">
            <div className="text-[10px] uppercase font-bold text-slate-400 mb-1 flex items-center space-x-1">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
              <span>Hemodynamic State</span>
            </div>
            <p className="text-slate-800 font-medium">{h.stabilization_status}</p>
          </div>
        )}
      </div>

      {h.diagnoses && h.diagnoses.length > 0 && (
        <div className="p-4 bg-white border border-slate-200 rounded-lg text-xs">
          <div className="text-[10px] uppercase font-bold text-slate-400 mb-2 flex items-center space-x-1">
            <Stethoscope className="w-3.5 h-3.5 text-sky-600" />
            <span>Discharge Diagnoses Matrix</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {h.diagnoses.map((d: string, idx: number) => (
              <span
                key={idx}
                className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md font-medium text-[11px]"
              >
                {d}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
