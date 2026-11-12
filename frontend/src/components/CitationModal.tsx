import React from "react";
import { X, BookOpen, Quote, ShieldAlert, CheckCircle2, XCircle } from "lucide-react";
import { VerificationResult } from "../types";

interface CitationModalProps {
  isOpen: boolean;
  onClose: () => void;
  verification: VerificationResult | null;
  medicationName: string;
}

export const CitationModal: React.FC<CitationModalProps> = ({
  isOpen,
  onClose,
  verification,
  medicationName,
}) => {
  if (!isOpen || !verification) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-xl w-full p-6 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-sky-100 text-sky-700 rounded-lg">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base">Grounded Formulary Citation</h3>
              <p className="text-xs text-slate-500">
                Verification claim audit for <span className="font-semibold text-slate-800">{medicationName}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Citation Body */}
        <div className="py-4 space-y-4 text-xs">
          {/* Metadata Bar */}
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span className="text-slate-400 font-medium">Source Document: </span>
              <span className="font-semibold text-slate-800">Meridian Bay Institutional Formulary Digest (Rev 8.2)</span>
            </div>
            <div>
              <span className="text-slate-400 font-medium">Section: </span>
              <span className="font-semibold text-sky-700">{verification.citation_section || "General"}</span>
            </div>
          </div>

          {/* Verbatim Grounded Passage */}
          <div>
            <div className="flex items-center space-x-1.5 text-slate-500 font-bold uppercase tracking-wider text-[10px] mb-1.5">
              <Quote className="w-3.5 h-3.5 text-sky-600" />
              <span>Verbatim Authoritative Formulary Passage</span>
            </div>
            <blockquote className="p-4 bg-sky-50/60 border-l-4 border-sky-500 rounded-r-lg text-slate-800 leading-relaxed italic text-xs">
              "{verification.citation_passage || "No specific passage retrieved."}"
            </blockquote>
          </div>

          {/* Verification Verdict */}
          <div className="p-3 bg-white border border-slate-200 rounded-lg">
            <div className="text-[10px] uppercase font-bold text-slate-400 mb-1">Clinical Verdict & Rationale</div>
            <p className="text-slate-800 font-medium leading-relaxed">{verification.explanation}</p>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium text-xs transition"
          >
            Close Citation
          </button>
        </div>
      </div>
    </div>
  );
};
