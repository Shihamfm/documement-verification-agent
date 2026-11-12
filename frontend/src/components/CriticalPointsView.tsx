import React from "react";
import { AlertTriangle, Clock, ShieldAlert, Calendar, CheckSquare, Info } from "lucide-react";
import { CriticalPoint } from "../types";

interface CriticalPointsViewProps {
  criticalPoints: CriticalPoint[];
}

export const CriticalPointsView: React.FC<CriticalPointsViewProps> = ({ criticalPoints }) => {
  if (!criticalPoints || criticalPoints.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400">
        <CheckSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-xs">No critical points extracted.</p>
      </div>
    );
  }

  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case "High":
        return "bg-rose-50 text-rose-700 border-rose-200 ring-rose-200";
      case "Medium":
        return "bg-amber-50 text-amber-700 border-amber-200 ring-amber-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200 ring-slate-200";
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "urgent_adverse_effect":
      case "safety_precaution":
        return <ShieldAlert className="w-4 h-4 text-rose-600" />;
      case "abrupt_cessation_warning":
        return <AlertTriangle className="w-4 h-4 text-amber-600" />;
      case "timing_critical":
        return <Clock className="w-4 h-4 text-sky-600" />;
      case "follow_up":
      case "lab_monitoring":
        return <Calendar className="w-4 h-4 text-indigo-600" />;
      default:
        return <Info className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-slate-100 text-xs text-slate-500">
        <p>Ranked items the patient must not miss (grounded strictly in primary document):</p>
        <span className="font-semibold text-slate-700">{criticalPoints.length} Action Items</span>
      </div>

      <div className="space-y-2.5">
        {criticalPoints.map((pt, idx) => (
          <div
            key={pt.id || idx}
            className="p-3.5 bg-white border border-slate-200 rounded-xl hover:border-slate-300 transition shadow-2xs"
          >
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <div className="flex items-center space-x-2">
                <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-mono text-slate-600">
                  {idx + 1}
                </span>
                <span className="flex items-center space-x-1.5 font-semibold text-xs text-slate-900">
                  {getCategoryIcon(pt.category)}
                  <span className="capitalize">{pt.category.replace(/_/g, " ")}</span>
                </span>
              </div>

              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wide ${getSeverityStyle(
                  pt.severity
                )}`}
              >
                {pt.severity} Priority
              </span>
            </div>

            <p className="text-xs text-slate-800 font-medium leading-relaxed mb-2 pl-7">
              {pt.point_text}
            </p>

            {/* Verbatim Source Quote */}
            <div className="pl-7 text-[11px] text-slate-500 italic bg-slate-50/80 p-2 rounded border border-slate-100">
              <span className="font-semibold not-italic text-slate-600">Primary Source: </span>
              "{pt.source_quote}"
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
