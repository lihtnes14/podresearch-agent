import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import PipelineStepper from './components/PipelineStepper';
import InputForm from './components/InputForm';
import ArticleEditor from './components/ArticleEditor';
import EditorialFeedback from './components/EditorialFeedback';
import FinalApprovalView from './components/FinalApprovalView';
import {
  checkHealth,
  generateArticle,
  getSession,
  saveHumanReview,
  requestRevision,
  approveArticle,
} from './api';
import { AlertCircle } from 'lucide-react';

export default function App() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [revising, setRevising] = useState(false);
  const [approving, setApproving] = useState(false);
  const [savingDirectEdits, setSavingDirectEdits] = useState(false);
  const [decisions, setDecisions] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);

  // Initial health check
  useEffect(() => {
    checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));

    const interval = setInterval(() => {
      checkHealth()
        .then(() => setIsHealthy(true))
        .catch(() => setIsHealthy(false));
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  // 1. Kick off full pipeline: Agent 1 -> Agent 2 -> Agent 3
  const handleStartGeneration = async (payload) => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const data = await generateArticle(payload);
      setSession(data);
      setDecisions({});
    } catch (err) {
      setErrorMessage(err.message || 'Generation failed');
    } finally {
      setLoading(false);
    }
  };

  // 2. Decision change on Agent 3 issues
  const handleDecisionChange = (index, decisionObj) => {
    setDecisions((prev) => ({
      ...prev,
      [index]: decisionObj,
    }));
  };

  // 3. Save direct markdown edits
  const handleSaveDirectEdits = async (newContent) => {
    if (!session) return;
    setSavingDirectEdits(true);
    try {
      const res = await saveHumanReview(session.session_id, Object.values(decisions), newContent);
      // Update local session state
      setSession((prev) => ({
        ...prev,
        article: {
          ...prev.article,
          markdown_article: newContent,
          content: newContent,
        },
      }));
    } catch (err) {
      setErrorMessage(err.message || 'Failed to save direct edits');
    } finally {
      setSavingDirectEdits(false);
    }
  };

  // 4. Request another revision from Agent 2 using selected feedback
  const handleRequestRevision = async (additionalInstructions) => {
    if (!session) return;
    setRevising(true);
    setErrorMessage(null);
    try {
      // Collect issues marked 'accept' or with custom notes
      const selectedFeedback = [];
      const issues = session.review?.issues || [];
      issues.forEach((issue, idx) => {
        const dec = decisions[idx];
        if (dec && dec.action === 'accept') {
          selectedFeedback.push({
            ...issue,
            custom_instruction: dec.note || null,
          });
        }
      });

      const currentArticleContent =
        session.article?.markdown_article || session.article?.content || session.final_article || '';
      const data = await requestRevision(
        session.session_id,
        selectedFeedback,
        currentArticleContent,
        additionalInstructions
      );

      // Fetch fresh session to update version history and new review
      const refreshed = await getSession(session.session_id);
      setSession(refreshed);
      setDecisions({});
    } catch (err) {
      setErrorMessage(err.message || 'Revision request failed');
    } finally {
      setRevising(false);
    }
  };

  // 5. Approve article for publication
  const handleApprove = async () => {
    if (!session) return;
    setApproving(true);
    setErrorMessage(null);
    try {
      const currentArticleContent =
        session.article?.markdown_article || session.article?.content || session.final_article || '';
      const data = await approveArticle(
        session.session_id,
        currentArticleContent,
        'Approved by Human Editor'
      );
      setSession((prev) => ({
        ...prev,
        status: 'approved',
        final_article: data.final_article || currentArticleContent,
      }));
    } catch (err) {
      setErrorMessage(err.message || 'Failed to approve article');
    } finally {
      setApproving(false);
    }
  };

  const handleNewSession = () => {
    setSession(null);
    setDecisions({});
    setErrorMessage(null);
  };

  return (
    <div className="app-container">
      <Header
        isHealthy={isHealthy}
        onNewSession={handleNewSession}
        activeSessionId={session?.session_id}
      />

      <main className="main-content">
        {/* Stepper tracking Agent 1 -> Agent 2 -> Agent 3 -> Human Review -> Approved */}
        <PipelineStepper
          currentStatus={session?.status || 'idle'}
          isProcessing={loading || revising}
        />

        {/* Global Error Notice */}
        {errorMessage && (
          <div
            style={{
              background: 'var(--danger-bg)',
              border: '1px solid var(--danger)',
              color: '#fca5a5',
              padding: '12px 16px',
              borderRadius: '8px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <AlertCircle size={18} />
            <span style={{ fontSize: '13px' }}>{errorMessage}</span>
          </div>
        )}

        {/* View 1: Input Form when no session is active */}
        {!session && (
          <InputForm onSubmit={handleStartGeneration} loading={loading} />
        )}

        {/* View 2: Human-in-the-Loop Review Stage */}
        {session && session.status !== 'approved' && (
          <div className="review-grid">
            <ArticleEditor
              article={session.article}
              outline={session.outline}
              versions={session.history || []}
              onSaveDirectEdits={handleSaveDirectEdits}
              savingDirectEdits={savingDirectEdits}
            />

            <EditorialFeedback
              review={session.review}
              decisions={decisions}
              onDecisionChange={handleDecisionChange}
              onRequestRevision={handleRequestRevision}
              revising={revising}
              onApprove={handleApprove}
              approving={approving}
            />
          </div>
        )}

        {/* View 3: Final Approved Article & Ready to Publish */}
        {session && session.status === 'approved' && (
          <FinalApprovalView
            session={session}
            onBackToEdit={() => setSession((prev) => ({ ...prev, status: 'human_review' }))}
          />
        )}
      </main>
    </div>
  );
}
