import React from 'react';
import { Check, Clock, Edit3, ShieldAlert, FileText, CheckCircle2 } from 'lucide-react';

const STEPS = [
  { id: 'extract', label: '1. Extraction', desc: 'Transcript & 5m Chunks', icon: Clock },
  { id: 'analyst', label: '2. Agent 1', desc: 'Content Outline', icon: FileText },
  { id: 'writer', label: '3. Agent 2', desc: 'Article Writer', icon: Edit3 },
  { id: 'reviewer', label: '4. Agent 3', desc: 'Editorial Audit', icon: ShieldAlert },
  { id: 'human_review', label: '5. Human Review', desc: 'Decisions & Edits', icon: Edit3 },
  { id: 'approved', label: '6. Approved', desc: 'Ready to Publish', icon: CheckCircle2 },
];

export default function PipelineStepper({ currentStatus, isProcessing }) {
  const getStepState = (stepId, index) => {
    if (currentStatus === 'completed' || currentStatus === 'approved') return 'completed';

    if (currentStatus === 'human_review' || currentStatus === 'needs_human_review') {
      if (index < 4) return 'completed';
      if (index === 4) return 'active';
      return 'pending';
    }

    if (isProcessing) {
      if (index < 3) return 'completed';
      if (index === 3) return 'active';
      return 'pending';
    }

    return 'pending';
  };

  return (
    <div className="stepper">
      {STEPS.map((step, idx) => {
        const state = getStepState(step.id, idx);
        const Icon = step.icon;

        return (
          <React.Fragment key={step.id}>
            <div className={`step-item ${state}`}>
              <div className="step-circle">
                {state === 'completed' ? <Check size={16} /> : <Icon size={16} />}
              </div>
              <div className="step-info">
                <span className="step-name">{step.label}</span>
                <span className="step-desc">{step.desc}</span>
              </div>
            </div>
            {idx < STEPS.length - 1 && <div className="step-divider" />}
          </React.Fragment>
        );
      })}
    </div>
  );
}
