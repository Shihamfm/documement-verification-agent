import React, { useState, useEffect } from "react";
import {
  ArrowLeft,
  FileText,
  AlertTriangle,
  CheckCircle2,
  BookOpen,
  Sparkles,
  ShieldAlert,
  Loader2,
  Share2,
} from "lucide-react";
import {
  DocumentAnalysis,
  Job,
  TelemetryEvent,
  VerificationResult,
} from "../types";
import {
  getDocumentAnalysis,
  getJob,
  subscribeToJobEvents,
} from "../api/client";
import { PipelineTracker } from "../components/PipelineTracker";
import { DocumentViewer } from "../components/DocumentViewer";
import { SummaryView } from "../components/SummaryView";
import { CriticalPointsView } from "../components/CriticalPointsView";
import { FlaggedIssuesList } from "../components/FlaggedIssuesList";
import { ReferenceViewer } from "../components/ReferenceViewer";
import { CitationModal } from "../components/CitationModal";

interface DocumentViewPageProps {
  documentId: string;
  initialJobId?: string;
  onBack: () => void;
}

export const DocumentViewPage: React.FC<DocumentViewPageProps> = ({
  documentId,
  initialJobId,
  onBack,
}) => {
  const [analysis, setAnalysis] = useState<DocumentAnalysis | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [currentStage, setCurrentStage] = useState<string>("pending");
  const [progressPct, setProgressPct] = useState<number>(0);
  const [stagesTelemetry, setStagesTelemetry] = useState<
    Array<{ stage_name: string; status: string; duration_seconds: number }>
  >([]);
  const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
  const [activeTab, setActiveTab] = useState<"issues" | "summary" | "critical" | "reference">("issues");

  // Citation modal state
  const [isCitationOpen, setIsCitationOpen] = useState<boolean>(false);
  const [activeCitation, setActiveCitation] = useState<VerificationResult | null>(null);
  const [activeCitationMed, setActiveCitationMed] = useState<string>("");

  // Deep-link reference navigation state
  const [targetMonograph, setTargetMonograph] = useState<string | null>(null);

  // Load Job and Subscribe to SSE
  useEffect(() => {
    let unsubscribeSSE: (() => void) | null = null;

    const setupTelemetry = async () => {
      let activeJobId = initialJobId;

      if (!activeJobId) {
        try {
          const loadedAnalysis = await getDocumentAnalysis(documentId);
          setAnalysis(loadedAnalysis);
          setProgressPct(100);
          setCurrentStage("done");
          return;
        } catch (e) {
          // Analysis not ready yet, continue looking for job
        }
      }

      if (activeJobId) {
        try {
          const j = await getJob(activeJobId);
          setJob(j);
          setCurrentStage(j.current_stage);
          if (j.status === "completed") {
            setProgressPct(100);
            loadAnalysisData();
          } else if (j.stages) {
            setStagesTelemetry(
              j.stages.map((s) => ({
                stage_name: s.stage_name,
                status: s.status,
                duration_seconds: s.duration_seconds,
              }))
            );
          }

          // Connect SSE stream
          unsubscribeSSE = subscribeToJobEvents(
            activeJobId,
            (event: TelemetryEvent) => {
              setCurrentStage(event.stage_name);
              setProgressPct(event.progress_percentage || 0);

              if (event.stages) {
                setStagesTelemetry(event.stages);
              }

              if (event.error_message) {
                setErrorMessage(event.error_message);
              }

              if (event.status === "completed" || event.stage_name === "done") {
                setProgressPct(100);
                loadAnalysisData();
              }
            },
            (err) => {
              console.warn("SSE connection closed or re-establishing:", err);
            }
          );
        } catch (err) {
          console.error("Failed to load initial job:", err);
        }
      } else {
        loadAnalysisData();
      }
    };

    setupTelemetry();

    return () => {
      if (unsubscribeSSE) unsubscribeSSE();
    };
  }, [documentId, initialJobId]);

  const loadAnalysisData = async () => {
    try {
      const data = await getDocumentAnalysis(documentId);
      setAnalysis(data);
    } catch (err) {
      console.error("Failed to fetch document analysis:", err);
    }
  };

  const handleOpenCitation = (v: VerificationResult, medName: string) => {
    setActiveCitation(v);
    setActiveCitationMed(medName);
    setIsCitationOpen(true);
  };

  const handleDeepLinkReference = (monographName: string, sectionTitle: string) => {
    setTargetMonograph(monographName);
    setActiveTab("reference");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Top Navigation Bar */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={onBack}
          className="flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <div className="flex items-center space-x-2">
          {analysis && (
            <div className="flex items-center space-x-2 text-xs">
              <span className="px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 font-bold">
                {analysis.contradicted_count} Contradictions
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">
                {analysis.supported_count} Supported
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold">
                {analysis.unsupported_count} Unsupported
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Real-time Observable Pipeline Tracker */}
      <PipelineTracker
        job={job}
        currentStage={currentStage}
        progressPercentage={progressPct}
        stagesTelemetry={stagesTelemetry}
        errorMessage={errorMessage}
      />

      {/* Main Dual-Pane Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Pane: Primary Document (5 cols) */}
        <div className="lg:col-span-5 h-[calc(100vh-14rem)] sticky top-20">
          {analysis ? (
            <DocumentViewer
              analysis={analysis}
              onSelectMedication={(med) => {
                setActiveTab("issues");
              }}
            />
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 h-full flex items-center justify-center p-8 text-center text-slate-400">
              <div>
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-sky-600" />
                <p className="text-xs">Parsing and rendering primary document...</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Pane: Verification Workbench Tabs (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col min-h-[calc(100vh-14rem)]">
          {/* Workbench Tabs Header */}
          <div className="p-3 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setActiveTab("issues")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  activeTab === "issues"
                    ? "bg-white text-sky-700 shadow-2xs border border-slate-200"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <ShieldAlert className="w-4 h-4 text-rose-500" />
                <span>Formulary Verification</span>
                {analysis && (
                  <span className="ml-1 px-1.5 py-0.2 bg-rose-100 text-rose-800 rounded-full text-[10px]">
                    {analysis.contradicted_count}
                  </span>
                )}
              </button>

              <button
                onClick={() => setActiveTab("critical")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  activeTab === "critical"
                    ? "bg-white text-sky-700 shadow-2xs border border-slate-200"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                <span>Critical Points</span>
                {analysis && (
                  <span className="ml-1 px-1.5 py-0.2 bg-slate-200 text-slate-700 rounded-full text-[10px]">
                    {analysis.critical_points.length}
                  </span>
                )}
              </button>

              <button
                onClick={() => setActiveTab("summary")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  activeTab === "summary"
                    ? "bg-white text-sky-700 shadow-2xs border border-slate-200"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Sparkles className="w-4 h-4 text-sky-600" />
                <span>Executive Summary</span>
              </button>

              <button
                onClick={() => setActiveTab("reference")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  activeTab === "reference"
                    ? "bg-white text-sky-700 shadow-2xs border border-slate-200"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <BookOpen className="w-4 h-4 text-indigo-500" />
                <span>Formulary Inspector</span>
              </button>
            </div>
          </div>

          {/* Workbench Tab Content */}
          <div className="p-6 overflow-y-auto flex-1">
            {!analysis && progressPct < 100 ? (
              <div className="py-24 text-center text-slate-400">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3 text-sky-600" />
                <h4 className="text-sm font-semibold text-slate-700">Verification in progress</h4>
                <p className="text-xs text-slate-500 mt-1">
                  Stages are executing asynchronously: {currentStage.replace(/_/g, " ")}
                </p>
              </div>
            ) : analysis ? (
              <>
                {activeTab === "issues" && (
                  <FlaggedIssuesList
                    entities={analysis.prescribed_entities}
                    onOpenCitation={handleOpenCitation}
                    onDeepLinkReference={handleDeepLinkReference}
                  />
                )}

                {activeTab === "critical" && (
                  <CriticalPointsView criticalPoints={analysis.critical_points} />
                )}

                {activeTab === "summary" && (
                  <SummaryView summary={analysis.summary} />
                )}

                {activeTab === "reference" && (
                  <ReferenceViewer
                    targetMonograph={targetMonograph}
                    onClearTarget={() => setTargetMonograph(null)}
                  />
                )}
              </>
            ) : (
              <div className="p-8 text-center text-slate-400 text-xs">
                No analysis data available.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Grounded Citation Preview Modal */}
      <CitationModal
        isOpen={isCitationOpen}
        onClose={() => setIsCitationOpen(false)}
        verification={activeCitation}
        medicationName={activeCitationMed}
      />
    </div>
  );
};
