import { useState } from "react";
import { generateClinicalSummary } from "./api";
import { ClinicalSummary } from "./components/ClinicalSummary";
import { IntakeForm } from "./components/IntakeForm";
import type { ClinicalSummaryResponse, IntakeFormData } from "./types";
import "./App.css";

const initialForm: IntakeFormData = {
  patientId: "",
  chiefComplaint: "",
  nurseNotes: "",
  smoker: false,
  alcoholUse: false,
  drugUse: false,
  laboratoryReview: true,
  riskAssessment: true,
  costEstimate: false,
};

export default function App() {
  const [form, setForm] = useState<IntakeFormData>(initialForm);
  const [summary, setSummary] = useState<ClinicalSummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);

    try {
      const result = await generateClinicalSummary(form);
      setSummary(result);
    } catch (err) {
      setSummary(null);
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__brand">
          <div className="app-header__logo" aria-hidden="true">
            <svg viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="#2563EB" />
              <path
                d="M16 8V24M10 14H22"
                stroke="white"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            </svg>
          </div>
          <div>
            <h1>Clinical Decision Support</h1>
            <p>Multi-agent intake and summary for walk-in and urgent care</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="app-layout">
          <div className="app-layout__form">
            {error && (
              <div className="app-error" role="alert">
                {error}
              </div>
            )}
            <IntakeForm
              form={form}
              loading={loading}
              onChange={(updates) => setForm((current) => ({ ...current, ...updates }))}
              onSubmit={handleGenerate}
            />
          </div>
          <div className="app-layout__summary">
            <ClinicalSummary summary={summary} loading={loading} />
          </div>
        </div>
      </main>

      <footer className="app-footer">
        For clinical decision support only. Verify all findings before patient discussion.
      </footer>
    </div>
  );
}
