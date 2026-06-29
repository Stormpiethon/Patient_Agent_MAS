import type { FormEvent } from "react";
import { AnalysisCheckbox } from "./AnalysisCheckbox";
import { ToggleSwitch } from "./ToggleSwitch";
import type { IntakeFormData } from "../types";
import "./IntakeForm.css";

interface IntakeFormProps {
  form: IntakeFormData;
  loading: boolean;
  onChange: (updates: Partial<IntakeFormData>) => void;
  onSubmit: () => void;
}

export function IntakeForm({ form, loading, onChange, onSubmit }: IntakeFormProps) {
  const hasAnalysisSelected =
    form.laboratoryReview || form.riskAssessment || form.costEstimate;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className="intake-form" onSubmit={handleSubmit}>
      <section className="intake-form__section card">
        <header className="section-header">
          <h2>Patient Intake</h2>
          <p>Enter visit details to begin clinical analysis.</p>
        </header>

        <div className="field-grid">
          <div className="field">
            <label htmlFor="patient-id">Patient ID</label>
            <input
              id="patient-id"
              type="text"
              placeholder="Example: jd-014"
              value={form.patientId}
              onChange={(event) => onChange({ patientId: event.target.value })}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="chief-complaint">Chief Complaint</label>
            <input
              id="chief-complaint"
              type="text"
              placeholder="Chest pain, fatigue, dizziness"
              value={form.chiefComplaint}
              onChange={(event) => onChange({ chiefComplaint: event.target.value })}
              required
            />
          </div>
        </div>

        <div className="field">
          <label htmlFor="nurse-notes">Nurse Notes</label>
          <textarea
            id="nurse-notes"
            rows={4}
            placeholder="Enter additional observations..."
            value={form.nurseNotes}
            onChange={(event) => onChange({ nurseNotes: event.target.value })}
          />
        </div>
      </section>

      <section className="intake-form__section card">
        <header className="section-header">
          <h2>Lifestyle Assessment</h2>
          <p>Indicate relevant lifestyle factors for risk analysis.</p>
        </header>

        <div className="toggle-grid">
          <ToggleSwitch
            id="smoker"
            label="Current Smoker"
            checked={form.smoker}
            onChange={(checked) => onChange({ smoker: checked })}
          />
          <ToggleSwitch
            id="alcohol"
            label="Alcohol Use"
            checked={form.alcoholUse}
            onChange={(checked) => onChange({ alcoholUse: checked })}
          />
          <ToggleSwitch
            id="drug-use"
            label="Recreational Drug Use"
            checked={form.drugUse}
            onChange={(checked) => onChange({ drugUse: checked })}
          />
        </div>
      </section>

      <section className="intake-form__section card">
        <header className="section-header">
          <h2>Requested Analysis</h2>
          <p>Select one or more analyses to run for this visit.</p>
        </header>

        <div className="analysis-grid">
          <AnalysisCheckbox
            id="labs"
            label="Laboratory Review"
            description="Review lab values and identify potential concerns."
            checked={form.laboratoryReview}
            onChange={(checked) => onChange({ laboratoryReview: checked })}
          />
          <AnalysisCheckbox
            id="risk"
            label="Risk Assessment"
            description="Evaluate cardiovascular and metabolic risk factors."
            checked={form.riskAssessment}
            onChange={(checked) => onChange({ riskAssessment: checked })}
          />
          <AnalysisCheckbox
            id="cost"
            label="Cost Estimate"
            description="Estimate medication and procedure costs."
            checked={form.costEstimate}
            onChange={(checked) => onChange({ costEstimate: checked })}
          />
        </div>
      </section>

      <button
        type="submit"
        className="generate-button"
        disabled={loading || !form.patientId.trim() || !hasAnalysisSelected}
      >
        {loading ? "Generating Summary..." : "Generate Clinical Summary"}
      </button>
    </form>
  );
}
