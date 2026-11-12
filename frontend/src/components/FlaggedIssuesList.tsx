import React, { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  BookOpen,
  ArrowRight,
  Filter,
  ExternalLink,
  ChevronRight,
  Clock,
  Calendar,
  Pill,
} from "lucide-react";
import { PrescribedEntity, VerificationResult } from "../types";

interface FlaggedIssuesListProps {
  entities: PrescribedEntity[];
  onOpenCitation: (verification: VerificationResult, medName: string) => void;
  onDeepLinkReference?: (monographName: string, sectionTitle: string) => void;
}

export const FlaggedIssuesList: React.FC<FlaggedIssuesListProps> = ({
  entities,
  onOpenCitation,
  onDeepLinkReference,
}) => {
  const [filter, setFilter] = useState<string>("all");

  const filtered = entities.filter((e) => {
    if (filter === "all") return true;
    return e.verification?.status.toLowerCase() === filter.toLowerCase();
  });

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case "Supported":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Supported</span>
          </span>
        );
      case "Contradicted":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">
            <XCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>Contradicted</span>
          </span>
        );
      case "Unsupported":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
            <span>Unsupported</span>
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-600 font-medium">
            Pending
          </span>
        );
    }
  };

  return (
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg text-xs">
          <button
            onClick={() => setFilter("all")}
            className={`px-3 py-1 rounded-md font-medium transition ${
              filter === "all" ? "bg-white text-slate-900 shadow-2xs" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            All ({entities.length})
          </button>
          <button
            onClick={() => setFilter("contradicted")}
            className={`px-3 py-1 rounded-md font-medium transition ${
              filter === "contradicted" ? "bg-white text-rose-700 shadow-2xs font-bold" : "text-slate-600 hover:text-rose-700"
            }`}
          >
            Contradicted ({entities.filter((e) => e.verification?.status === "Contradicted").length})
          </button>
          <button
            onClick={() => setFilter("supported")}
            className={`px-3 py-1 rounded-md font-medium transition ${
              filter === "supported" ? "bg-white text-emerald-700 shadow-2xs font-bold" : "text-slate-600 hover:text-emerald-700"
            }`}
          >
            Supported ({entities.filter((e) => e.verification?.status === "Supported").length})
          </button>
          <button
            onClick={() => setFilter("unsupported")}
            className={`px-3 py-1 rounded-md font-medium transition ${
              filter === "unsupported" ? "bg-white text-amber-700 shadow-2xs font-bold" : "text-slate-600 hover:text-amber-700"
            }`}
          >
            Unsupported ({entities.filter((e) => e.verification?.status === "Unsupported").length})
          </button>
        </div>

        <span className="text-[11px] text-slate-400 hidden sm:inline">
          Formulary Revision 8.2 Ground Truth
        </span>
      </div>

      {/* Medication Verification Cards */}
      <div className="space-y-3">
        {filtered.map((entity) => {
          const v = entity.verification;
          const isContradicted = v?.status === "Contradicted";
          const isUnsupported = v?.status === "Unsupported";

          return (
            <div
              key={entity.id}
              className={`p-4 rounded-xl border transition-all ${
                isContradicted
                  ? "bg-rose-50/30 border-rose-200 hover:border-rose-300 shadow-xs"
                  : isUnsupported
                  ? "bg-amber-50/20 border-amber-200 hover:border-amber-300"
                  : "bg-white border-slate-200 hover:border-slate-300"
              }`}
            >
              {/* Header: Drug Name + Status */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-sm text-slate-900">{entity.medication_name}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">
                      {entity.dose} {entity.route}
                    </span>
                    <span className="text-xs text-slate-500">• {entity.frequency}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">
                    Duration: <span className="font-medium text-slate-700">{entity.duration}</span> • Indication:{" "}
                    <span className="font-medium text-slate-700">{entity.indication}</span>
                  </div>
                </div>

                <div>{getStatusBadge(v?.status)}</div>
              </div>

              {/* Clinical Explanation */}
              {v && (
                <div
                  className={`mt-2 p-3 rounded-lg text-xs leading-relaxed ${
                    isContradicted
                      ? "bg-rose-100/60 text-rose-950 font-medium"
                      : isUnsupported
                      ? "bg-amber-100/50 text-amber-950"
                      : "bg-slate-50 text-slate-700"
                  }`}
                >
                  {v.explanation}
                </div>
              )}

              {/* Parameter Discordance / Concordance Breakdown */}
              {v?.parameter_matches?.details && Object.keys(v.parameter_matches.details).length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-100">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Prescribing Parameter Evaluation
                  </div>
                  <div className="space-y-1 text-xs">
                    {Object.entries(v.parameter_matches.details).map(([param, detail]: [string, any]) => (
                      <div
                        key={param}
                        className="flex flex-col sm:flex-row sm:items-center justify-between p-2 rounded bg-white/80 border border-slate-100 gap-1 text-[11px]"
                      >
                        <span className="font-semibold text-slate-700 capitalize">{param} comparison:</span>
                        <div className="flex items-center space-x-2 text-slate-600">
                          {detail.prescribed && (
                            <span className="line-through text-rose-600 font-mono">{detail.prescribed}</span>
                          )}
                          {detail.formulary_standard && (
                            <span className="text-emerald-700 font-semibold font-mono">
                              → {detail.formulary_standard}
                            </span>
                          )}
                          {detail.concordance && (
                            <span className="text-emerald-600 font-medium">{detail.concordance}</span>
                          )}
                          {detail.conflict && (
                            <span className="text-rose-700 font-semibold">({detail.conflict})</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons: View Citation & Deep-Link Reference */}
              {v && (
                <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="text-[11px] text-slate-500 font-medium">
                    Cited: <span className="text-slate-800">{v.citation_section || "Formulary Digest"}</span>
                  </div>

                  <div className="flex items-center space-x-2">
                    {/* Clickable Citation Preview Button */}
                    <button
                      onClick={() => onOpenCitation(v, entity.medication_name)}
                      className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium flex items-center space-x-1 transition text-[11px]"
                    >
                      <BookOpen className="w-3.5 h-3.5 text-sky-600" />
                      <span>Inspect Citation</span>
                    </button>

                    {/* Extra Credit: Deep Link into Reference Document */}
                    {v.citation_monograph && onDeepLinkReference && (
                      <button
                        onClick={() =>
                          onDeepLinkReference(v.citation_monograph || "", v.citation_section || "")
                        }
                        className="px-2.5 py-1 rounded bg-sky-50 hover:bg-sky-100 text-sky-700 font-semibold flex items-center space-x-1 transition text-[11px]"
                      >
                        <ExternalLink className="w-3.5 h-3.5 text-sky-600" />
                        <span>View in Reference</span>
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
