import type { ChangeEvent } from "react";
import "./ToggleSwitch.css";

interface ToggleSwitchProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export function ToggleSwitch({
  id,
  label,
  checked,
  onChange,
}: ToggleSwitchProps) {
  return (
    <label className="toggle-switch" htmlFor={id}>
      <span className="toggle-switch__label">{label}</span>
      <span className="toggle-switch__control">
        <input
          id={id}
          type="checkbox"
          role="switch"
          checked={checked}
          onChange={(event: ChangeEvent<HTMLInputElement>) =>
            onChange(event.target.checked)
          }
        />
        <span className="toggle-switch__track" aria-hidden="true">
          <span className="toggle-switch__thumb" />
        </span>
      </span>
    </label>
  );
}
