import React, { useState } from "react";
import { User, Calendar, FileText, Stethoscope, AlertTriangle, Pill, Clock } from "lucide-react";
import { DocumentAnalysis } from "../types";

interface DocumentViewerProps {
  analysis: DocumentAnalysis;
  onSelectMedication?: (medName: string) => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  analysis,
  onSelectMedication,
}) => {
  const [activeTab, setActiveTab] = useState<string>("formatted");
  const p = analysis.patient_info || {};

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-full overflow-hidden">
      {/* Pane Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-sky-600" />
          <h2 className="font-semibold text-sm text-slate-900">Primary Discharge Summary</h2>
          <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">
            {analysis.filename}
          </span>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center space-x-1 bg-slate-200/80 p-0.5 rounded-lg text-xs">
          <button
            onClick={() => setActiveTab("formatted")}
            className={`px-2.5 py-1 rounded-md font-medium transition ${
              activeTab === "formatted"
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Clinical View
          </button>
          <button
            onClick={() => setActiveTab("raw")}
            className={`px-2.5 py-1 rounded-md font-medium transition ${
              activeTab === "raw"
                ? "bg-white text-slate-900 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Original Text
          </button>
        </div>
      </div>

      {/* Patient Banner */}
      <div className="p-4 bg-sky-50/40 border-b border-sky-100 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Patient</div>
          <div className="font-bold text-slate-900 mt-0.5 flex items-center space-x-1">
            <User className="w-3.5 h-3.5 text-sky-600" />
            <span>{p.patient_name || "Daniel Okonkwo"}</span>
          </div>
          <div className="text-[10px] text-slate-500">{p.age || 58}yo {p.gender || "male"} • MRN {p.mrn || "MBMC-7714209"}</div>
        </div>

        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Admission</div>
          <div className="font-medium text-slate-800 mt-0.5 flex items-center space-x-1">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>{p.admission_date || "March 4, 2026"}</span>
          </div>
          <div className="text-[10px] text-slate-500">To {p.discharge_date || "March 11, 2026"}</div>
        </div>

        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Attending</div>
          <div className="font-medium text-slate-800 mt-0.5 flex items-center space-x-1">
            <Stethoscope className="w-3.5 h-3.5 text-slate-400" />
            <span>{p.attending || "Dr. R. Nakashima, MD"}</span>
          </div>
          <div className="text-[10px] text-slate-500">{p.service || "Internal Medicine"}</div>
        </div>

        <div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Status</div>
          <div className="mt-0.5 inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800">
            Discharged Home • Stable
          </div>
        </div>
      </div>

      {/* Document Content Scroll Area */}
      <div className="p-6 overflow-y-auto flex-1 text-xs leading-relaxed space-y-6">
        {activeTab === "formatted" ? (
          <>
            {/* 1. Reason for Admission */}
            <section className="border-b border-slate-100 pb-4">
              <h3 className="font-bold text-slate-900 text-sm mb-2 flex items-center space-x-1.5">
                <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-mono">1</span>
                <span>Reason for Admission</span>
              </h3>
              <p className="text-slate-700">
                Mr. Okonkwo, a 58-year-old man with a past history significant for borderline hypertension and dyslipidemia,
                presented to the emergency department on March 4 with a five-day history of progressive dyspnea on exertion,
                intermittent palpitations, and one episode of chest tightness lasting approximately twenty minutes that resolved
                spontaneously. Initial blood pressure on presentation was 188/104 mmHg, heart rate was 112 beats per minute and
                irregular, and oxygen saturation was 96% on room air. Initial ECG demonstrated atrial fibrillation with rapid
                ventricular response. Troponin was mildly elevated on first measurement and trended down on serial draws; the patient
                was ruled out for acute coronary syndrome.
              </p>
            </section>

            {/* 2. Hospital Course */}
            <section className="border-b border-slate-100 pb-4">
              <h3 className="font-bold text-slate-900 text-sm mb-2 flex items-center space-x-1.5">
                <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-mono">2</span>
                <span>Hospital Course</span>
              </h3>
              <p className="text-slate-700">
                The patient was admitted to the internal medicine service for management of newly diagnosed atrial fibrillation,
                hypertensive urgency, and ongoing dyslipidemia. Rate control was achieved with intravenous medication on day one,
                then transitioned to oral therapy on day two. Blood pressure was titrated downward over the course of the admission,
                reaching a stable range of 128–134 / 78–84 mmHg by day five. The patient also reported worsening anxiety in
                association with his new diagnoses, which was discussed with the inpatient psychiatry consultation service; a short
                course of anxiolytic therapy was recommended.
              </p>
            </section>

            {/* 3. Discharge Diagnoses */}
            <section className="border-b border-slate-100 pb-4">
              <h3 className="font-bold text-slate-900 text-sm mb-2 flex items-center space-x-1.5">
                <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-mono">3</span>
                <span>Discharge Diagnoses</span>
              </h3>
              <ul className="list-decimal list-inside space-y-1 text-slate-700 font-medium">
                <li>New-onset atrial fibrillation, rate-controlled</li>
                <li>Hypertensive urgency, resolved</li>
                <li>Hyperlipidemia</li>
                <li>Acute anxiety, situational, related to new cardiovascular diagnoses</li>
                <li>GERD, mild — prophylaxis given concurrent medication burden</li>
              </ul>
            </section>

            {/* 4. Discharge Medications Table */}
            <section className="border-b border-slate-100 pb-4">
              <h3 className="font-bold text-slate-900 text-sm mb-2 flex items-center space-x-1.5">
                <span className="w-5 h-5 rounded-full bg-sky-100 text-sky-800 flex items-center justify-center text-[10px] font-mono">4</span>
                <span>Prescribed Discharge Regimen</span>
                <span className="text-[10px] text-slate-400 font-normal">({analysis.prescribed_entities.length} medications)</span>
              </h3>

              <div className="overflow-x-auto border border-slate-200 rounded-lg">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold text-slate-700">
                      <th className="p-2">Medication</th>
                      <th className="p-2">Dose</th>
                      <th className="p-2">Route / Frequency</th>
                      <th className="p-2">Duration</th>
                      <th className="p-2">Indication</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {analysis.prescribed_entities.map((m) => (
                      <tr
                        key={m.id}
                        onClick={() => onSelectMedication && onSelectMedication(m.medication_name)}
                        className="hover:bg-sky-50/50 cursor-pointer transition"
                      >
                        <td className="p-2 font-bold text-sky-900 flex items-center space-x-1">
                          <Pill className="w-3.5 h-3.5 text-sky-600" />
                          <span>{m.medication_name}</span>
                        </td>
                        <td className="p-2 font-mono text-slate-800">{m.dose}</td>
                        <td className="p-2 text-slate-700">{m.frequency}</td>
                        <td className="p-2 text-slate-700">{m.duration}</td>
                        <td className="p-2 text-slate-600">{m.indication}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* 5. Patient Counseling & Warnings */}
            <section className="border-b border-slate-100 pb-4">
              <h3 className="font-bold text-slate-900 text-sm mb-2 flex items-center space-x-1.5">
                <span className="w-5 h-5 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center text-[10px] font-mono">5</span>
                <span>Counseling and Warnings Reviewed with Patient</span>
              </h3>
              <ul className="space-y-2 text-slate-700">
                <li className="flex items-start space-x-2">
                  <span className="text-amber-500 font-bold">•</span>
                  <span><strong>Velantine:</strong> May cause persistent dry cough; patient advised to report promptly.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-amber-500 font-bold">•</span>
                  <span><strong>Cordizem-XR:</strong> May cause fatigue; must take consistently in morning and NOT stop abruptly.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-amber-500 font-bold">•</span>
                  <span><strong>Pravoxil:</strong> Report unexplained muscle pain or weakness immediately.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-amber-500 font-bold">•</span>
                  <span><strong>Etrazolam:</strong> May cause drowsiness; do not drive. 8-week course discussed.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-amber-500 font-bold">•</span>
                  <span><strong>Quintaxin:</strong> Take thirty minutes before breakfast for optimal effect.</span>
                </li>
              </ul>
            </section>

            {/* 6. Follow-Up */}
            <section>
              <h3 className="font-bold text-slate-900 text-sm mb-2 flex items-center space-x-1.5">
                <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-mono">6</span>
                <span>Follow-Up & Laboratory Schedule</span>
              </h3>
              <p className="text-slate-700">
                Follow up with primary care within 7 days, cardiology within 2 weeks, and outpatient psychiatry within 2 weeks.
                Repeat BMP in 2 weeks for renal function on ACE inhibitor. Repeat lipid panel in 6 weeks for Pravoxil response.
              </p>
            </section>
          </>
        ) : (
          <pre className="whitespace-pre-wrap font-mono text-[11px] text-slate-700 bg-slate-50 p-4 rounded-lg border border-slate-200">
            {analysis.raw_text}
          </pre>
        )}
      </div>
    </div>
  );
};
