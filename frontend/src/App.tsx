import React, { useState, useEffect } from "react";
import { User } from "./types";
import { getCurrentUser } from "./api/client";
import { Navbar } from "./components/Navbar";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DocumentViewPage } from "./pages/DocumentViewPage";

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState<boolean>(true);
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | undefined>(undefined);

  // Check existing session
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      getCurrentUser()
        .then((user) => setCurrentUser(user))
        .catch(() => {
          localStorage.removeItem("auth_token");
          setCurrentUser(null);
        })
        .finally(() => setIsAuthLoading(false));
    } else {
      setIsAuthLoading(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    setCurrentUser(null);
    setActiveDocumentId(null);
    setActiveJobId(undefined);
  };

  const handleOpenDocument = (documentId: string, jobId?: string) => {
    setActiveDocumentId(documentId);
    setActiveJobId(jobId);
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="w-8 h-8 border-3 border-sky-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!currentUser) {
    return <LoginPage onLoginSuccess={(user) => setCurrentUser(user)} />;
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar
        currentUser={currentUser}
        onLogout={handleLogout}
        onGoHome={() => {
          setActiveDocumentId(null);
          setActiveJobId(undefined);
        }}
        activeViewTitle={activeDocumentId ? "Clinical Audit Workbench" : undefined}
      />

      <main className="flex-1">
        {activeDocumentId ? (
          <DocumentViewPage
            documentId={activeDocumentId}
            initialJobId={activeJobId}
            onBack={() => {
              setActiveDocumentId(null);
              setActiveJobId(undefined);
            }}
          />
        ) : (
          <DashboardPage
            currentUser={currentUser}
            onOpenDocument={handleOpenDocument}
          />
        )}
      </main>
    </div>
  );
};

export default App;
