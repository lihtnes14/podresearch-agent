import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RotateCcw,
  CheckCheck,
  Filter,
  MessageSquare,
  Sparkles,
} from 'lucide-react';

export default function EditorialFeedback({
  review,
  decisions,
  onDecisionChange,
  onRequestRevision,
  revising,
  onApprove,
  approving,
}) {
  const [filterType, setFilterType] = useState('all');
  const [additionalNote, setAdditionalNote] = useState('');

  if (!review) {
    return (
      <div className="card">
        <p style={{ color: 'var(--text-muted)' }}>No editorial review available yet.</p>
      </div>
    );
  }

  const issues = review.issues || [];

  const filteredIssues = issues.filter((issue) => {
    if (filterType === 'all') return true;
    return issue.type === filterType;
  });

  const getDecision = (idx) => {
    return decisions[idx] || { action: 'pending', note: '' };
  };

  const setDecisionAction = (idx, action) => {
    const current = getDecision(idx);
    onDecisionChange(idx, { ...current, action });
  };

  const setDecisionNote = (idx, note) => {
    const current = getDecision(idx);
    onDecisionChange(idx, { ...current, note });
  };

  const acceptedCount = Object.values(decisions).filter((d) => d.action === 'accept').length;
  const rejectedCount = Object.values(decisions).filter((d) => d.action === 'reject').length;

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header & Agent 3 Summary */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div className="card-title" style={{ marginBottom: 0 }}>
            <ShieldAlert size={20} style={{ color: review.approved ? 'var(--success)' : 'var(--warning)' }} />
            <span>Agent 3 Editorial Review</span>
          </div>

          <span
            className={`badge ${review.approved ? 'badge-low' : 'badge-high'}`}
            style={{ fontSize: '12px', padding: '4px 10px' }}
          >
            {review.approved ? '✓ Article Approved by QC' : '⚠ Action Recommended'}
          </span>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', background: 'var(--bg-primary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
          <strong>Assessment:</strong> {review.overall_feedback || 'Review completed.'}
        </p>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '8px', marginBottom: '12px' }}>
        <button
          className={`btn btn-sm ${filterType === 'all' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setFilterType('all')}
        >
          All ({issues.length})
        </button>
        <button
          className={`btn btn-sm ${filterType === 'unsupported_claim' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setFilterType('unsupported_claim')}
        >
          Unsupported Claims
        </button>
        <button
          className={`btn btn-sm ${filterType === 'technical_concern' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setFilterType('technical_concern')}
        >
          Technical Concerns
        </button>
      </div>

      {/* Issues List */}
      <div style={{ flex: 1, overflowY: 'auto', maxHeight: '420px', paddingRight: '4px' }}>
        {filteredIssues.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--text-muted)' }}>
            <CheckCircle size={32} style={{ color: 'var(--success)', marginBottom: '8px' }} />
            <p>No issues found for this filter.</p>
          </div>
        ) : (
          filteredIssues.map((issue, idx) => {
            const decision = getDecision(idx);
            return (
              <div
                key={idx}
                className={`issue-card ${
                  decision.action === 'accept' ? 'accepted' : decision.action === 'reject' ? 'rejected' : ''
                }`}
              >
                <div className="issue-header">
                  <span className={`badge badge-${issue.severity || 'medium'}`}>
                    {issue.severity || 'medium'}
                  </span>
                  <span className="issue-type">{issue.type?.replace('_', ' ')}</span>
                  {issue.timestamp && (
                    <span className="issue-timestamp">@{issue.timestamp}</span>
                  )}
                </div>

                <div className="issue-section">{issue.section || 'General'}</div>
                <div className="issue-desc">{issue.issue}</div>

                <div className="decision-actions">
                  <button
                    className={`btn btn-sm ${decision.action === 'accept' ? 'btn-success' : 'btn-outline'}`}
                    onClick={() => setDecisionAction(idx, 'accept')}
                  >
                    <CheckCircle size={13} />
                    <span>Accept (Fix in Revision)</span>
                  </button>

                  <button
                    className={`btn btn-sm ${decision.action === 'reject' ? 'btn-danger' : 'btn-outline'}`}
                    onClick={() => setDecisionAction(idx, 'reject')}
                  >
                    <XCircle size={13} />
                    <span>Reject (Keep as is)</span>
                  </button>
                </div>

                <div style={{ marginTop: '8px' }}>
                  <input
                    type="text"
                    className="form-input"
                    style={{ fontSize: '12px', padding: '6px 10px' }}
                    placeholder="Optional: custom edit instruction for this issue..."
                    value={decision.note || ''}
                    onChange={(e) => setDecisionNote(idx, e.target.value)}
                  />
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Human-in-the-Loop Actions */}
      <div style={{ borderTop: '1px solid var(--border)', paddingTop: '16px', marginTop: '16px' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '10px' }}>
          Decisions: <strong style={{ color: 'var(--success)' }}>{acceptedCount} accepted</strong>,{' '}
          <strong style={{ color: 'var(--danger)' }}>{rejectedCount} rejected</strong>
        </div>

        <div className="form-group" style={{ marginBottom: '12px' }}>
          <input
            type="text"
            className="form-input"
            style={{ fontSize: '13px' }}
            placeholder="Add general instructions for Agent 2's revision..."
            value={additionalNote}
            onChange={(e) => setAdditionalNote(e.target.value)}
            disabled={revising}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <button
            className="btn btn-primary"
            onClick={() => onRequestRevision(additionalNote)}
            disabled={revising || approving}
            title="Sends accepted feedback to Agent 2 to produce an updated draft"
          >
            {revising ? (
              <>
                <div className="spinner" />
                <span>Revising Draft...</span>
              </>
            ) : (
              <>
                <RotateCcw size={15} />
                <span>Request Revision</span>
              </>
            )}
          </button>

          <button
            className="btn btn-success"
            onClick={onApprove}
            disabled={approving || revising}
            title="Approve article and mark ready for publication"
          >
            {approving ? (
              <>
                <div className="spinner" />
                <span>Approving...</span>
              </>
            ) : (
              <>
                <CheckCheck size={16} />
                <span>Approve & Publish</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
