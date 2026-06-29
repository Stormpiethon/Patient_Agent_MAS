import type { ClinicalSummaryResponse } from "../types";
import "./ClinicalSummary.css";

interface ClinicalSummaryProps {
  summary: ClinicalSummaryResponse | null;
  loading: boolean;
}

function statusClass(status: string): string {
  if (status === "normal") return "status-normal";
  if (status === "high") return "status-high";
  if (status === "low") return "status-low";
  return "status-neutral";
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function lifestyleLabel(value: boolean): string {
  return value ? "Yes" : "No";
}

function parseRiskSummary(summary: string): string {
  const trimmed = summary.trim();
  if (!trimmed.startsWith("{")) {
    return summary;
  }

  try {
    const parsed = JSON.parse(trimmed) as {
      one_line_summary?: string;
      risk_level_summary?: string;
      key_drivers?: string[];
    };

    const parts: string[] = [];
    if (parsed.one_line_summary) {
      parts.push(parsed.one_line_summary);
    } else if (parsed.risk_level_summary) {
      parts.push(`${parsed.risk_level_summary} risk identified.`);
    }

    return parts.join(" ") || summary;
  } catch {
    return summary;
  }
}

export function ClinicalSummary({ summary, loading }: ClinicalSummaryProps) {
  if (loading) {
    return (
      <aside className="clinical-summary card">
        <div className="clinical-summary__loading">
          <div className="spinner" aria-hidden="true" />
          <p>Preparing clinician summary...</p>
          <span className="clinical-summary__loading-hint">
            Running selected analyses and synthesizing results.
          </span>
        </div>
      </aside>
    );
  }

  if (!summary) {
    return (
      <aside className="clinical-summary card clinical-summary--empty">
        <div className="clinical-summary__placeholder">
          <div className="clinical-summary__icon" aria-hidden="true">
            <svg viewBox="0 0 48 48" fill="none">
              <rect x="8" y="6" width="32" height="36" rx="4" stroke="currentColor" strokeWidth="2" />
              <path d="M16 16H32M16 24H28M16 32H24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <h2>Clinical Summary</h2>
          <p>
            Complete patient intake and select requested analyses. The clinician-ready
            summary will appear here.
          </p>
        </div>
      </aside>
    );
  }

  const { patient, requested_analyses: requested } = summary;

  return (
    <aside className="clinical-summary card">
      <header className="clinical-summary__header">
        <div>
          <span className="clinical-summary__eyebrow">Clinician Dashboard</span>
          <h2>Clinical Summary</h2>
        </div>
        <span className="clinical-summary__badge">Ready for Review</span>
      </header>

      <div className="summary-section">
        <h3>Patient Information</h3>
        <dl className="info-grid">
          <div>
            <dt>Patient ID</dt>
            <dd>{patient.patient_id}</dd>
          </div>
          {patient.name && (
            <div>
              <dt>Name</dt>
              <dd>{patient.name}</dd>
            </div>
          )}
          {patient.age != null && (
            <div>
              <dt>Age</dt>
              <dd>{patient.age}</dd>
            </div>
          )}
          {patient.gender && (
            <div>
              <dt>Gender</dt>
              <dd>{patient.gender}</dd>
            </div>
          )}
        </dl>
        {patient.previous_conditions && patient.previous_conditions.length > 0 && (
          <div className="tag-list">
            {patient.previous_conditions.map((condition) => (
              <span key={condition} className="tag">
                {condition}
              </span>
            ))}
          </div>
        )}
        <dl className="info-grid info-grid--compact">
          <div>
            <dt>Current Smoker</dt>
            <dd>{lifestyleLabel(summary.lifestyle.smoker)}</dd>
          </div>
          <div>
            <dt>Alcohol Use</dt>
            <dd>{lifestyleLabel(summary.lifestyle.alcohol_use)}</dd>
          </div>
          <div>
            <dt>Recreational Drug Use</dt>
            <dd>{lifestyleLabel(summary.lifestyle.drug_use)}</dd>
          </div>
        </dl>
      </div>

      <div className="summary-section">
        <h3>Chief Complaint</h3>
        <p className="summary-text">{summary.chief_complaint || "Not documented."}</p>
        {summary.nurse_notes && (
          <>
            <h4 className="summary-subheading">Nurse Notes</h4>
            <p className="summary-text">{summary.nurse_notes}</p>
          </>
        )}
      </div>

      {requested.laboratory_review && summary.laboratory_findings && (
        <div className="summary-section">
          <h3>Laboratory Findings</h3>
          <div className="table-wrap">
            <table className="lab-table">
              <thead>
                <tr>
                  <th>Test</th>
                  <th>Value</th>
                  <th>Reference</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {summary.laboratory_findings.map((finding) => (
                  <tr key={finding.lab_id}>
                    <td>{finding.name}</td>
                    <td>
                      {finding.value} {finding.unit}
                    </td>
                    <td>
                      {finding.reference_low}–{finding.reference_high} {finding.unit}
                    </td>
                    <td>
                      <span className={`status-pill ${statusClass(finding.status)}`}>
                        {finding.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {requested.laboratory_review && summary.potential_health_concerns && (
        <div className="summary-section">
          <h3>Potential Health Concerns</h3>
          <ul className="concern-list">
            {summary.potential_health_concerns.map((concern, index) => (
              <li key={`${concern}-${index}`}>{concern}</li>
            ))}
          </ul>
        </div>
      )}

      {requested.risk_assessment && summary.risk_assessment && (
        <div className="summary-section">
          <h3>Risk Assessment</h3>
          <div className="risk-header">
            <div className="risk-score">
              <span className="risk-score__value">{summary.risk_assessment.risk_score}</span>
              <span className="risk-score__label">Risk Score</span>
            </div>
            <span
              className={`risk-level risk-level--${summary.risk_assessment.risk_level?.toLowerCase() ?? "unknown"}`}
            >
              {summary.risk_assessment.risk_level ?? "Unknown"} Risk
            </span>
          </div>
          {(summary.risk_assessment.risk_factors?.length ?? 0) > 0 && (
            <div className="tag-list">
              {summary.risk_assessment.risk_factors?.map((factor) => (
                <span key={factor} className="tag tag--warning">
                  {factor}
                </span>
              ))}
            </div>
          )}
          <p className="summary-text">
            {parseRiskSummary(summary.risk_assessment.summary)}
          </p>
        </div>
      )}

      {requested.cost_estimate && summary.estimated_costs && (
        <div className="summary-section">
          <h3>Estimated Costs</h3>
          <div className="cost-total">
            Estimated Total: {formatCurrency(summary.estimated_costs.total_cost)}
          </div>
          {summary.estimated_costs.line_items.length > 0 && (
            <div className="table-wrap">
              <table className="lab-table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Type</th>
                    <th>Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.estimated_costs.line_items.map((item, index) => (
                    <tr key={`${item.name}-${index}`}>
                      <td>
                        {item.name}
                        {item.dose ? ` (${item.dose})` : ""}
                      </td>
                      <td className="capitalize">{item.type}</td>
                      <td>
                        {item.unit_cost != null
                          ? formatCurrency(item.unit_cost)
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="summary-text">{summary.estimated_costs.summary}</p>
        </div>
      )}

      <div className="summary-section summary-section--highlight">
        <h3>Recommended Discussion</h3>
        <div className="discussion-content">
          {(summary.recommended_discussion ?? "").split("\n").map((paragraph, index) => {
            const trimmed = paragraph.trim();
            if (!trimmed) return null;
            return <p key={index}>{trimmed}</p>;
          })}
        </div>
      </div>
    </aside>
  );
}
