import React, { useState } from "react";
import { ShieldCheck, Lock, Mail, User, AlertCircle, ArrowRight, Sparkles } from "lucide-react";
import { loginUser, registerUser } from "../api/client";
import { User as UserType } from "../types";

interface LoginPageProps {
  onLoginSuccess: (user: UserType) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [isSignUp, setIsSignUp] = useState<boolean>(false);
  const [email, setEmail] = useState<string>("reviewer@meridianbay.org");
  const [password, setPassword] = useState<string>("ReviewerPassword123!");
  const [fullName, setFullName] = useState<string>("Dr. Clinical Reviewer");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsLoading(true);

    try {
      if (isSignUp) {
        await registerUser(email, password, fullName);
      }
      const auth = await loginUser(email, password);
      onLoginSuccess({
        id: auth.user_id,
        email: auth.email,
        full_name: auth.full_name,
        created_at: new Date().toISOString(),
      });
    } catch (err: any) {
      setErrorMsg(err.message || "Authentication failed. Please verify credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreFillReviewer = () => {
    setEmail("reviewer@meridianbay.org");
    setPassword("ReviewerPassword123!");
    setIsSignUp(false);
    setErrorMsg(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="bg-sky-600 text-white p-3 rounded-2xl shadow-md">
            <ShieldCheck className="w-10 h-10" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-extrabold text-slate-900 tracking-tight">
          Meridian Bay Medical Center
        </h2>
        <p className="mt-1 text-center text-xs text-slate-600">
          Inpatient Formulary Verification & Clinical Safety Agent
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-sm border border-slate-200 sm:rounded-2xl sm:px-10">
          {/* Quick Reviewer Demo Fill Pill */}
          <div className="mb-6 p-3 bg-sky-50/70 border border-sky-100 rounded-xl flex items-center justify-between">
            <div>
              <div className="text-[11px] font-bold text-sky-900 flex items-center space-x-1">
                <Sparkles className="w-3.5 h-3.5 text-sky-600" />
                <span>Assignment Reviewer Access</span>
              </div>
              <div className="text-[10px] text-slate-500">Seed account pre-configured with test datasets</div>
            </div>
            <button
              type="button"
              onClick={handlePreFillReviewer}
              className="px-2.5 py-1 bg-white hover:bg-sky-50 text-sky-700 text-[11px] font-semibold rounded-md border border-sky-200 transition shadow-2xs"
            >
              Autofill
            </button>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            {isSignUp && (
              <div>
                <label className="block text-xs font-semibold text-slate-700">Full Name & Title</label>
                <div className="mt-1 relative rounded-md shadow-2xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-4 w-4 text-slate-400" />
                  </div>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="block w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500 focus:border-sky-500"
                    placeholder="Dr. Jane Smith, MD"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-700">Email Address</label>
              <div className="mt-1 relative rounded-md shadow-2xs">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500 focus:border-sky-500"
                  placeholder="reviewer@meridianbay.org"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700">Password</label>
              <div className="mt-1 relative rounded-md shadow-2xs">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500 focus:border-sky-500"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            {errorMsg && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 mt-0.5 text-rose-600 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 transition"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : isSignUp ? (
                "Create Clinical Account"
              ) : (
                "Sign In to Verification Portal"
              )}
            </button>
          </form>

          {/* Toggle between Sign In / Sign Up */}
          <div className="mt-6 pt-4 border-t border-slate-100 text-center">
            <button
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setErrorMsg(null);
              }}
              className="text-xs text-sky-600 hover:text-sky-800 font-semibold transition"
            >
              {isSignUp ? "Already have an account? Sign In" : "Need a new account? Sign Up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
