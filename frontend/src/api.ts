import type { ClinicalSummaryResponse, IntakeFormData } from "./types";

export async function generateClinicalSummary(
  form: IntakeFormData,
): Promise<ClinicalSummaryResponse> {
  const response = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      patient_id: form.patientId.trim(),
      chief_complaint: form.chiefComplaint.trim(),
      nurse_notes: form.nurseNotes.trim(),
      smoker: form.smoker,
      alcohol_use: form.alcoholUse,
      drug_use: form.drugUse,
      laboratory_review: form.laboratoryReview,
      risk_assessment: form.riskAssessment,
      cost_estimate: form.costEstimate,
    }),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      data?.detail ??
      (typeof data === "string" ? data : "Unable to generate clinical summary.");
    throw new Error(message);
  }

  return data as ClinicalSummaryResponse;
}
