export interface IntakeFormData {
  patientId: string;
  chiefComplaint: string;
  nurseNotes: string;
  smoker: boolean;
  alcoholUse: boolean;
  drugUse: boolean;
  laboratoryReview: boolean;
  riskAssessment: boolean;
  costEstimate: boolean;
}

export interface LabFinding {
  lab_id: string;
  name: string;
  value: number;
  unit: string;
  reference_low: number;
  reference_high: number;
  status: string;
}

export interface CostLineItem {
  type: string;
  name: string;
  dose?: string;
  unit_cost: number | null;
  cost_period?: string;
  status: string;
}

export interface ClinicalSummaryResponse {
  patient: {
    patient_id: string;
    name?: string;
    age?: number;
    gender?: string;
    previous_conditions?: string[];
  };
  chief_complaint: string;
  nurse_notes: string;
  lifestyle: {
    smoker: boolean;
    alcohol_use: boolean;
    drug_use: boolean;
  };
  requested_analyses: {
    laboratory_review: boolean;
    risk_assessment: boolean;
    cost_estimate: boolean;
  };
  laboratory_findings?: LabFinding[];
  potential_health_concerns?: string[];
  risk_assessment?: {
    risk_score: number;
    risk_level: string;
    risk_factors: string[];
    summary: string;
  };
  estimated_costs?: {
    line_items: CostLineItem[];
    total_cost: number;
    summary: string;
  };
  recommended_discussion: string;
}
