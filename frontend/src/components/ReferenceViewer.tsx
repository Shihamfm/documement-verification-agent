import React, { useState, useEffect, useRef } from "react";
import { BookOpen, Search, ShieldCheck, ChevronDown, ChevronRight, Hash } from "lucide-react";

interface ReferenceViewerProps {
  targetMonograph?: string | null;
  onClearTarget?: () => void;
}

export const ReferenceViewer: React.FC<ReferenceViewerProps> = ({
  targetMonograph,
  onClearTarget,
}) => {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const itemRefs = useRef<Record<string, HTMLDivElement | null>>({});

  useEffect(() => {
    if (targetMonograph) {
      const key = targetMonograph.toLowerCase().trim();
      const el = itemRefs.current[key];
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.classList.add("highlight-target");
        const timer = setTimeout(() => {
          el.classList.remove("highlight-target");
          if (onClearTarget) onClearTarget();
        }, 3000);
        return () => clearTimeout(timer);
      }
    }
  }, [targetMonograph, onClearTarget]);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-full overflow-hidden">
      {/* Header & Search */}
      <div className="p-4 border-b border-slate-200 bg-slate-50/70">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-sky-600" />
            <h3 className="font-semibold text-sm text-slate-900">Institutional Formulary Digest</h3>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">
            Rev 8.2 • Feb 2026
          </span>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search formulary monographs, indications, dosage limits..."
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
        </div>
      </div>

      {/* Monographs Content */}
      <div className="p-6 overflow-y-auto flex-1 space-y-8 text-xs leading-relaxed">
        {/* Preface */}
        <section className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-slate-600">
          <h4 className="font-bold text-slate-800 mb-1">Preface & Institutional Scope</h4>
          <p>
            Maintained by the Meridian Bay Medical Center Pharmacy & Therapeutics Committee. Represents the
            authoritative institutional reference for adult inpatient prescribing. Where institutional guidance
            differs from manufacturer labeling, this guidance reflects committee consensus.
          </p>
        </section>

        {/* Section I. Cardiovascular Agents */}
        <section className="space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <span className="text-[10px] uppercase font-bold text-sky-600 tracking-wider">Section I</span>
            <h4 className="font-bold text-slate-900 text-sm">Cardiovascular Agents</h4>
          </div>

          {/* Velantine */}
          <div
            ref={(el) => (itemRefs.current["velantine"] = el)}
            className="p-4 rounded-xl border border-slate-200 bg-white space-y-2 transition-all"
          >
            <div className="flex items-center justify-between">
              <h5 className="font-bold text-base text-slate-900">Velantine</h5>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
                ACE Inhibitor
              </span>
            </div>
            <p className="text-slate-700"><strong>Indication:</strong> First-line antihypertensive in adult patients without contraindication.</p>
            <p className="text-slate-800 bg-emerald-50/50 p-2 rounded border border-emerald-100">
              <strong>Standard adult dose:</strong> 10 mg orally once daily. Initial dose may be reduced to 5 mg in mild renal impairment. Titrate at intervals ≥ 2 weeks. <strong>Max dose:</strong> 40 mg daily.
            </p>
            <p className="text-slate-600"><strong>Contraindications:</strong> Pregnancy (teratogenic). History of angioedema with ACE inhibitor. Bilateral renal artery stenosis. Concurrent ARB.</p>
            <p className="text-slate-600"><strong>Monitoring:</strong> Serum creatinine and potassium within 1–2 weeks of initiation.</p>
          </div>

          {/* Cordizem-XR */}
          <div
            ref={(el) => (itemRefs.current["cordizem-xr"] = el)}
            className="p-4 rounded-xl border border-slate-200 bg-white space-y-2 transition-all"
          >
            <div className="flex items-center justify-between">
              <h5 className="font-bold text-base text-slate-900">Cordizem-XR</h5>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
                Non-DHP CCB, Extended Release
              </span>
            </div>
            <p className="text-slate-700"><strong>Indication:</strong> Rate control in atrial fibrillation and atrial flutter. Second-line antihypertensive.</p>
            <p className="text-slate-800 bg-rose-50/50 p-2 rounded border border-rose-100">
              <strong>Standard adult dose:</strong> 50 mg orally once daily, taken in the morning. May be titrated upward in increments of 25 mg at intervals of no less than two weeks based on heart rate response. Sustained-release; must not be crushed. <strong>Max dose:</strong> 200 mg daily.
            </p>
            <p className="text-slate-600"><strong>Contraindications:</strong> Severe bradycardia (HR &lt; 50 bpm). 2nd/3rd degree AV block without pacemaker.</p>
          </div>

          {/* Mirosartan */}
          <div
            ref={(el) => (itemRefs.current["mirosartan"] = el)}
            className="p-4 rounded-xl border border-slate-200 bg-white space-y-2 transition-all"
          >
            <div className="flex items-center justify-between">
              <h5 className="font-bold text-base text-slate-900">Mirosartan</h5>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
                Angiotensin II Receptor Blocker (ARB)
              </span>
            </div>
            <p className="text-slate-700"><strong>Standard dose:</strong> 80 mg orally once daily. Titrate upward every 2+ weeks. Max 160 mg daily.</p>
            <p className="text-rose-700 bg-rose-50 p-2 rounded border border-rose-200">
              <strong>CRITICAL CONTRAINDICATION:</strong> Concurrent use with an ACE inhibitor (including Velantine) is strictly contraindicated due to lack of additional benefit and substantially increased risk of renal impairment, hypotension, and hyperkalemia.
            </p>
          </div>
        </section>

        {/* Section II. Lipid-Lowering Agents */}
        <section className="space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <span className="text-[10px] uppercase font-bold text-sky-600 tracking-wider">Section II</span>
            <h4 className="font-bold text-slate-900 text-sm">Lipid-Lowering Agents</h4>
          </div>

          {/* Pravoxil */}
          <div
            ref={(el) => (itemRefs.current["pravoxil"] = el)}
            className="p-4 rounded-xl border border-slate-200 bg-white space-y-2 transition-all"
          >
            <div className="flex items-center justify-between">
              <h5 className="font-bold text-base text-slate-900">Pravoxil</h5>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
                HMG-CoA Reductase Inhibitor (Statin)
              </span>
            </div>
            <p className="text-slate-700"><strong>Indication:</strong> Primary and secondary prevention of atherosclerotic cardiovascular disease.</p>
            <p className="text-slate-900 bg-amber-50/70 p-2 rounded border border-amber-200">
              <strong>Standard adult dose:</strong> 20 mg orally once daily, <strong>at bedtime</strong>. Pravoxil's pharmacokinetics favor evening administration to align peak inhibition with nighttime endogenous cholesterol synthesis. <em>Morning administration substantially reduces therapeutic effect.</em>
            </p>
            <p className="text-slate-700"><strong>Prescribing notes:</strong> Patients should be counseled to take Pravoxil at bedtime, not in the morning. Report unexplained muscle pain or weakness immediately.</p>
          </div>
        </section>

        {/* Section III. Anxiolytics and Sedatives */}
        <section className="space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <span className="text-[10px] uppercase font-bold text-sky-600 tracking-wider">Section III</span>
            <h4 className="font-bold text-slate-900 text-sm">Anxiolytics and Sedatives</h4>
          </div>

          {/* Etrazolam */}
          <div
            ref={(el) => (itemRefs.current["etrazolam"] = el)}
            className="p-4 rounded-xl border border-slate-200 bg-white space-y-2 transition-all"
          >
            <div className="flex items-center justify-between">
              <h5 className="font-bold text-base text-slate-900">Etrazolam</h5>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
                Intermediate-Acting Benzodiazepine
              </span>
            </div>
            <p className="text-slate-700"><strong>Standard adult dose:</strong> 0.5 mg orally twice daily. Max 1 mg twice daily.</p>
            <p className="text-slate-900 bg-rose-50/80 p-2.5 rounded border border-rose-200">
              <strong>Prescribing notes (Duration Limit):</strong> Etrazolam is approved for short-term use only, defined as a treatment duration of <strong>up to 4 weeks</strong> including any taper period. Use beyond 4 weeks substantially increases risk of physical dependence. <em>Prescribers must not initiate Etrazolam with an intended duration beyond 4 weeks.</em>
            </p>
          </div>
        </section>

        {/* Section IV. Anticoagulants */}
        <section className="space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <span className="text-[10px] uppercase font-bold text-sky-600 tracking-wider">Section IV</span>
            <h4 className="font-bold text-slate-900 text-sm">Anticoagulants</h4>
          </div>

          <div
            ref={(el) => (itemRefs.current["sumavast"] = el)}
            className="p-4 rounded-xl border border-slate-200 bg-white space-y-2 transition-all"
          >
            <div className="flex items-center justify-between">
              <h5 className="font-bold text-base text-slate-900">Sumavast</h5>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
                Direct Oral Factor Xa Inhibitor (DOAC)
              </span>
            </div>
            <p className="text-slate-700"><strong>Indication:</strong> Stroke prevention in non-valvular atrial fibrillation. Standard dose 5 mg PO twice daily.</p>
          </div>
        </section>

        {/* Section V. Gastrointestinal Agents */}
        <section className="space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <span className="text-[10px] uppercase font-bold text-sky-600 tracking-wider">Section V</span>
            <h4 className="font-bold text-slate-900 text-sm">Gastrointestinal Agents</h4>
          </div>

          {/* Quintaxin */}
          <div
            ref={(el) => (itemRefs.current["quintaxin"] = el)}
            className="p-4 rounded-xl border border-slate-200 bg-white space-y-2 transition-all"
          >
            <div className="flex items-center justify-between">
              <h5 className="font-bold text-base text-slate-900">Quintaxin</h5>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
                Proton Pump Inhibitor (PPI)
              </span>
            </div>
            <p className="text-slate-700"><strong>Standard adult dose:</strong> 20 mg orally once daily, taken 30 minutes before breakfast.</p>
            <p className="text-slate-600"><strong>Monitoring:</strong> Review indication at 8 weeks. Continuation requires clinical justification.</p>
          </div>
        </section>

        {/* Section VII. Quick Reference & Unlisted Drugs */}
        <section className="space-y-4">
          <div className="border-b border-slate-200 pb-2">
            <span className="text-[10px] uppercase font-bold text-sky-600 tracking-wider">Section VII</span>
            <h4 className="font-bold text-slate-900 text-sm">Quick-Reference Summary & Unlisted Agents</h4>
          </div>

          <div
            ref={(el) => (itemRefs.current["unlisted"] = el)}
            className="p-4 rounded-xl border border-amber-200 bg-amber-50/40 space-y-2"
          >
            <h5 className="font-bold text-slate-900 text-xs">Drugs Not In This Digest</h5>
            <p className="text-slate-700 leading-relaxed text-xs">
              This digest contains institutional monographs for the eight medications listed. Other medications may
              be on formulary at Meridian Bay Medical Center but are not addressed in this digest. Prescribers
              requiring guidance on a medication not listed here (e.g. <strong>Pranixol</strong>) should contact the
              inpatient pharmacy directly. Do not infer prescribing parameters for unlisted medications from the
              entries above.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
};
