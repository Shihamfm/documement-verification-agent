import React from "react";
import { ShieldCheck, FileCheck, LogOut, User as UserIcon, Activity } from "lucide-react";
import { User } from "../types";

interface NavbarProps {
  currentUser: User | null;
  onLogout: () => void;
  onGoHome: () => void;
  activeViewTitle?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentUser,
  onLogout,
  onGoHome,
  activeViewTitle,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Title */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={onGoHome}>
          <div className="bg-sky-600 text-white p-2 rounded-lg shadow-sm">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">Meridian Bay</span>
              <span className="px-2 py-0.5 text-xs font-semibold bg-sky-100 text-sky-800 rounded">
                Formulary Verification Agent
              </span>
            </div>
            <p className="text-xs text-slate-500">Clinical Inpatient & Discharge Safety Assurance</p>
          </div>
        </div>

        {/* Center / Active Document Title */}
        {activeViewTitle && (
          <div className="hidden md:flex items-center space-x-2 px-3 py-1 bg-slate-100 rounded-md text-xs text-slate-700">
            <FileCheck className="w-4 h-4 text-sky-600" />
            <span className="font-medium truncate max-w-xs">{activeViewTitle}</span>
          </div>
        )}

        {/* User Profile & Actions */}
        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2 text-xs text-slate-600">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span>RAG Engine Active</span>
          </div>

          {currentUser ? (
            <div className="flex items-center space-x-3 border-l border-slate-200 pl-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-700 font-semibold text-xs">
                  <UserIcon className="w-4 h-4" />
                </div>
                <div className="text-left hidden lg:block">
                  <div className="text-xs font-semibold text-slate-900">{currentUser.full_name}</div>
                  <div className="text-[10px] text-slate-500">{currentUser.email}</div>
                </div>
              </div>
              <button
                onClick={onLogout}
                className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-md transition"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="text-xs text-slate-500">Not authenticated</div>
          )}
        </div>
      </div>
    </header>
  );
};
