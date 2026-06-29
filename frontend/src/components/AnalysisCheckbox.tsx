import type { ChangeEvent } from "react";
import "./AnalysisCheckbox.css";

interface AnalysisCheckboxProps {
  id: string;
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export function AnalysisCheckbox({
  id,
  label,
  description,
  checked,
  onChange,
}: AnalysisCheckboxProps) {
  return (
    <label className={`analysis-checkbox ${checked ? "is-checked" : ""}`} htmlFor={id}>
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(event: ChangeEvent<HTMLInputElement>) =>
          onChange(event.target.checked)
        }
      />
      <span className="analysis-checkbox__box" aria-hidden="true">
        {checked && (
          <svg viewBox="0 0 16 16" fill="none">
            <path
              d="M3.5 8.5L6.5 11.5L12.5 4.5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </span>
      <span className="analysis-checkbox__content">
        <span className="analysis-checkbox__label">{label}</span>
        <span className="analysis-checkbox__description">{description}</span>
      </span>
    </label>
  );
}
