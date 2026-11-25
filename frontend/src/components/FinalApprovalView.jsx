import React, { useState } from 'react';
import {
  CheckCircle2,
  Download,
  Copy,
  Check,
  ArrowLeft,
  ExternalLink,
  BookOpen,
  Sparkles,
  AlertCircle,
  Code2,
  Send,
} from 'lucide-react';
import { publishToMedium, publishToDevto } from '../api';

export default function FinalApprovalView({ session, onBackToEdit }) {
  const [copied, setCopied] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [activePlatform, setActivePlatform] = useState('devto'); // 'devto' | 'medium'
  const [showPublishConfig, setShowPublishConfig] = useState(false);

  // Dev.to state
  const [devtoApiKey, setDevtoApiKey] = useState(() => localStorage.getItem('devto_api_key') || '');
  const [devtoPublished, setDevtoPublished] = useState(false); // default draft
  const [devtoTags, setDevtoTags] = useState('ai, python, podcast, automation');
  const [devtoResult, setDevtoResult] = useState(null);

  // Medium state
  const [mediumToken, setMediumToken] = useState(() => localStorage.getItem('medium_integration_token') || '');
  const [mediumStatus, setMediumStatus] = useState('draft');
  const [mediumTags, setMediumTags] = useState('podcast, artificial-intelligence, tech');
  const [mediumResult, setMediumResult] = useState(null);

  const [publishError, setPublishError] = useState(null);

  const articleText =
    session.final_article || session.article?.markdown_article || session.article?.content || '';

  const handleCopy = () => {
    navigator.clipboard.writeText(articleText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([articleText], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = `${(session.article?.title || 'youtube-article')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handlePublishDevto = async () => {
    setPublishing(true);
    setPublishError(null);
    try {
      if (devtoApiKey.trim()) {
        localStorage.setItem('devto_api_key', devtoApiKey.trim());
      }
      const tags = devtoTags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);

      const res = await publishToDevto(session.session_id, {
        api_key: devtoApiKey.trim() || null,
        published: devtoPublished,
        tags,
        canonical_url: session.podcast_url || null,
      });

      setDevtoResult(res);
    } catch (err) {
      setPublishError(err.message || 'Failed to automate publish to Dev.to');
    } finally {
      setPublishing(false);
    }
  };

  const handlePublishMedium = async () => {
    setPublishing(true);
    setPublishError(null);
    try {
      if (mediumToken.trim()) {
        localStorage.setItem('medium_integration_token', mediumToken.trim());
      }
      const tags = mediumTags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);

      const res = await publishToMedium(session.session_id, {
        medium_token: mediumToken.trim() || null,
        publish_status: mediumStatus,
        tags,
        canonical_url: session.podcast_url || null,
      });

      setMediumResult(res);
    } catch (err) {
      setPublishError(err.message || 'Failed to publish to Medium');
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div style={{ maxWidth: '920px', margin: '0 auto' }}>
      {/* Publication Banner */}
      <div
        className="card"
        style={{
          marginBottom: '24px',
          border: '1px solid var(--success)',
          background: 'rgba(16, 185, 129, 0.05)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                background: 'var(--success)',
                color: 'white',
                borderRadius: '50%',
                padding: '8px',
                display: 'flex',
              }}
            >
              <CheckCircle2 size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700 }}>Publication Ready</h2>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                Article verified by Agent 3 and approved by Human Editorial Review.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button className="btn btn-outline btn-sm" onClick={onBackToEdit}>
              <ArrowLeft size={14} /> Back to Editor
            </button>
            <button className="btn btn-outline btn-sm" onClick={handleCopy}>
              {copied ? <Check size={14} /> : <Copy size={14} />}
              <span>{copied ? 'Copied' : 'Copy Markdown'}</span>
            </button>
            <button className="btn btn-outline btn-sm" onClick={handleDownload}>
              <Download size={14} /> Download .md
            </button>
            <button
              className="btn btn-success btn-sm"
              onClick={() => setShowPublishConfig(!showPublishConfig)}
              style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}
            >
              <Send size={14} /> Automate Blog Post 🚀
            </button>
          </div>
        </div>
      </div>

      {/* Automated Blog Publishing Card */}
      {showPublishConfig && (
        <div
          className="card"
          style={{
            marginBottom: '24px',
            border: '1px solid var(--primary)',
            background: 'var(--bg-secondary)',
          }}
        >
          {/* Platform Switcher Tabs */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                className={`btn btn-sm ${activePlatform === 'devto' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => { setActivePlatform('devto'); setPublishError(null); }}
              >
                <Code2 size={15} /> Dev.to (Instant API Automation - Recommended)
              </button>
              <button
                className={`btn btn-sm ${activePlatform === 'medium' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => { setActivePlatform('medium'); setPublishError(null); }}
              >
                <BookOpen size={15} /> Medium
              </button>
            </div>
          </div>

          {/* Global Error Banner */}
          {publishError && (
            <div
              style={{
                background: 'var(--danger-bg)',
                border: '1px solid var(--danger)',
                color: '#fca5a5',
                padding: '10px 14px',
                borderRadius: '6px',
                marginBottom: '16px',
                fontSize: '13px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <AlertCircle size={16} />
              <span>{publishError}</span>
            </div>
          )}

          {/* ============================================================== */}
          {/* PLATFORM 1: DEV.TO (Instant API Automation)                   */}
          {/* ============================================================== */}
          {activePlatform === 'devto' && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  Dev.to is the world's largest developer blogging network with <strong>instant free API access</strong>.
                </p>
                <a
                  href="https://dev.to/settings/extensions"
                  target="_blank"
                  rel="noreferrer"
                  style={{ fontSize: '12px', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '4px', whiteSpace: 'nowrap' }}
                >
                  <span>Generate Free API Key in 5s</span>
                  <ExternalLink size={12} />
                </a>
              </div>

              {devtoResult ? (
                <div
                  style={{
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid var(--success)',
                    borderRadius: '8px',
                    padding: '16px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <CheckCircle2 size={20} color="var(--success)" />
                    <h4 style={{ fontSize: '15px', color: 'var(--success)' }}>
                      🎉 Successfully Automated Post to Dev.to!
                    </h4>
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
                    Article status: <strong>{devtoResult.published ? 'Live Published' : 'Draft in Your Dashboard'}</strong> under{' '}
                    <strong>{devtoResult.author_name}</strong> (@{devtoResult.author_username}).
                  </p>
                  <a
                    href={devtoResult.post_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-success btn-sm"
                    style={{ textDecoration: 'none', display: 'inline-flex' }}
                  >
                    <ExternalLink size={14} /> Open Live Article on Dev.to
                  </a>
                </div>
              ) : (
                <div>
                  <div className="form-group">
                    <label className="form-label">
                      Dev.to API Key *
                    </label>
                    <input
                      type="password"
                      className="form-input"
                      placeholder="Paste your key from dev.to/settings/extensions"
                      value={devtoApiKey}
                      onChange={(e) => setDevtoApiKey(e.target.value)}
                      disabled={publishing}
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">Publish Mode</label>
                      <select
                        className="form-select"
                        value={devtoPublished ? 'true' : 'false'}
                        onChange={(e) => setDevtoPublished(e.target.value === 'true')}
                        disabled={publishing}
                      >
                        <option value="false">Save as Draft (Preview in your Dev.to dashboard)</option>
                        <option value="true">Publish Live (Immediately visible on Dev.to)</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Tags (up to 4 tags, comma-separated)</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="podcast, ai, python, tutorial"
                        value={devtoTags}
                        onChange={(e) => setDevtoTags(e.target.value)}
                        disabled={publishing}
                      />
                    </div>
                  </div>

                  <button
                    className="btn btn-primary"
                    onClick={handlePublishDevto}
                    disabled={publishing}
                    style={{ width: '100%', padding: '12px', fontSize: '14px' }}
                  >
                    {publishing ? (
                      <>
                        <div className="spinner" />
                        <span>Sending Article to Dev.to API...</span>
                      </>
                    ) : (
                      <>
                        <Send size={15} />
                        <span>Post Article to Dev.to ({devtoPublished ? 'LIVE' : 'DRAFT'})</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ============================================================== */}
          {/* PLATFORM 2: MEDIUM                                             */}
          {/* ============================================================== */}
          {activePlatform === 'medium' && (
            <div>
              <div style={{ background: 'var(--bg-primary)', padding: '12px 14px', borderRadius: '8px', marginBottom: '14px', border: '1px solid var(--border)' }}>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  💡 <strong>Tip for Medium:</strong> Since Medium closed self-service API keys for new users, you can use the instant 1-click method:
                </p>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button className="btn btn-primary btn-sm" onClick={handleCopy}>
                    {copied ? <Check size={13} /> : <Copy size={13} />}
                    <span>{copied ? 'Copied!' : '1. Copy Formatted Markdown'}</span>
                  </button>
                  <a
                    href="https://medium.com/new-story"
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-outline btn-sm"
                    style={{ textDecoration: 'none' }}
                  >
                    <ExternalLink size={13} /> 2. Open medium.com/new-story & Paste
                  </a>
                </div>
              </div>

              {mediumResult ? (
                <div
                  style={{
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid var(--success)',
                    borderRadius: '8px',
                    padding: '16px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <CheckCircle2 size={20} color="var(--success)" />
                    <h4 style={{ fontSize: '15px', color: 'var(--success)' }}>
                      Story Successfully Published to Medium!
                    </h4>
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Published as <strong>{mediumResult.publish_status}</strong> under{' '}
                    <strong>{mediumResult.author_name}</strong>.
                  </p>
                  <a
                    href={mediumResult.post_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-success btn-sm"
                    style={{ textDecoration: 'none', display: 'inline-flex' }}
                  >
                    <ExternalLink size={14} /> View Story on Medium
                  </a>
                </div>
              ) : (
                <div>
                  <div className="form-group">
                    <label className="form-label">
                      Medium Integration Token (If your account already has API access)
                    </label>
                    <input
                      type="password"
                      className="form-input"
                      placeholder="Paste your token from medium.com/me/settings/security"
                      value={mediumToken}
                      onChange={(e) => setMediumToken(e.target.value)}
                      disabled={publishing}
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">Publish Status</label>
                      <select
                        className="form-select"
                        value={mediumStatus}
                        onChange={(e) => setMediumStatus(e.target.value)}
                        disabled={publishing}
                      >
                        <option value="draft">Draft (Review before going live)</option>
                        <option value="public">Public</option>
                        <option value="unlisted">Unlisted</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Tags (comma-separated)</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="podcast, ai, tech"
                        value={mediumTags}
                        onChange={(e) => setMediumTags(e.target.value)}
                        disabled={publishing}
                      />
                    </div>
                  </div>

                  <button
                    className="btn btn-outline"
                    onClick={handlePublishMedium}
                    disabled={publishing}
                    style={{ width: '100%', padding: '10px' }}
                  >
                    {publishing ? (
                      <>
                        <div className="spinner" />
                        <span>Publishing to Medium API...</span>
                      </>
                    ) : (
                      <>
                        <BookOpen size={15} />
                        <span>Publish via Medium REST API</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Formatted Article Preview */}
      <div className="card">
        <div className="article-preview" style={{ maxHeight: 'none' }}>
          <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
            {articleText}
          </div>
        </div>
      </div>
    </div>
  );
}
