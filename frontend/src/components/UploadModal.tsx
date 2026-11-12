import React, { useState, useRef } from "react";
import { Upload, X, FileText, AlertCircle, Sparkles, CheckCircle2 } from "lucide-react";
import { uploadDocument } from "../api/client";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: (jobId: string, docId: string) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onUploadSuccess,
}) => {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  if (!isOpen) return null;

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    setErrorMsg(null);
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (ext !== "docx" && ext !== "pdf") {
      setErrorMsg("Invalid file format. Please upload a .docx or .pdf clinical document.");
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setErrorMsg("File size exceeds maximum threshold of 25MB.");
      return;
    }
    setSelectedFile(file);
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setErrorMsg(null);

    try {
      const resp = await uploadDocument(selectedFile);
      onUploadSuccess(resp.job_id, resp.document_id);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to upload document");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-lg w-full p-6 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-sky-100 text-sky-700 rounded-lg">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base">Upload Primary Discharge Summary</h3>
              <p className="text-xs text-slate-500">Ingest inpatient discharge summary for formulary verification</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Dropzone */}
        <div className="py-5">
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
              dragActive
                ? "border-sky-500 bg-sky-50/50"
                : selectedFile
                ? "border-emerald-400 bg-emerald-50/20"
                : "border-slate-300 hover:border-slate-400 bg-slate-50/50"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".docx,.pdf"
              onChange={handleFileChange}
              className="hidden"
            />

            {selectedFile ? (
              <div className="space-y-2">
                <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div className="font-semibold text-xs text-slate-900">{selectedFile.name}</div>
                <div className="text-[11px] text-slate-500 font-mono">
                  {(selectedFile.size / 1024).toFixed(1)} KB • Ready for asynchronous verification
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                  }}
                  className="text-xs text-rose-600 hover:underline pt-1"
                >
                  Change file
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <Upload className="w-8 h-8 text-slate-400 mx-auto" />
                <div className="text-xs font-semibold text-slate-700">
                  Drag and drop your clinical document here, or <span className="text-sky-600">browse</span>
                </div>
                <div className="text-[11px] text-slate-400">Supported formats: DOCX, PDF (up to 25MB)</div>
              </div>
            )}
          </div>

          {/* Reference Formulary Selector */}
          <div className="mt-4 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs flex items-center justify-between">
            <div>
              <div className="font-semibold text-slate-800">Target Formulary Reference</div>
              <div className="text-[11px] text-slate-500">Meridian Bay Institutional Formulary Digest (Rev 8.2)</div>
            </div>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-semibold">
              Default Active
            </span>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="mt-3 p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 mt-0.5 text-rose-600 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        {/* Modal Actions */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-medium transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!selectedFile || isUploading}
            className={`px-5 py-2 rounded-lg text-xs font-semibold text-white transition flex items-center space-x-2 ${
              !selectedFile || isUploading
                ? "bg-slate-300 cursor-not-allowed"
                : "bg-sky-600 hover:bg-sky-700 shadow-sm"
            }`}
          >
            {isUploading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Enqueuing Pipeline...</span>
              </>
            ) : (
              <span>Start Verification Pipeline</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
