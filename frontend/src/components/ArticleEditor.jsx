import React, { useState } from 'react';
import { Eye, Edit2, Copy, Check, Save, History, FileText } from 'lucide-react';

export default function ArticleEditor({
  article,
  onSaveDirectEdits,
  savingDirectEdits,
  versions = [],
  outline = null,
}) {
  const getArticleText = (art) => art?.markdown_article || art?.content || '';

  const [activeTab, setActiveTab] = useState('preview');
  const [editedContent, setEditedContent] = useState(getArticleText(article));
  const [copied, setCopied] = useState(false);

  // Sync if article content changes from props
  React.useEffect(() => {
    const text = getArticleText(article);
    if (text) {
      setEditedContent(text);
    }
  }, [article]);

  const handleCopy = () => {
    navigator.clipboard.writeText(editedContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveEdits = () => {
    if (onSaveDirectEdits) {
      onSaveDirectEdits(editedContent);
    }
  };

  const wordCount = editedContent.trim() ? editedContent.trim().split(/\s+/).length : 0;

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div className="tab-list" style={{ marginBottom: 0 }}>
          <button
            className={`tab-btn ${activeTab === 'preview' ? 'active' : ''}`}
            onClick={() => setActiveTab('preview')}
          >
            <Eye size={15} /> Preview
          </button>
          <button
            className={`tab-btn ${activeTab === 'edit' ? 'active' : ''}`}
            onClick={() => setActiveTab('edit')}
          >
            <Edit2 size={15} /> Edit Directly
          </button>
          {outline && (
            <button
              className={`tab-btn ${activeTab === 'outline' ? 'active' : ''}`}
              onClick={() => setActiveTab('outline')}
            >
              <FileText size={15} /> Agent 1 Outline
            </button>
          )}
          {versions.length > 0 && (
            <button
              className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <History size={15} /> Version History ({versions.length})
            </button>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{wordCount} words</span>
          <button className="btn btn-outline btn-sm" onClick={handleCopy} title="Copy Markdown">
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {activeTab === 'preview' && (
        <div className="article-preview">
          <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
            {editedContent}
          </div>
        </div>
      )}

      {activeTab === 'edit' && (
        <div>
          <textarea
            className="form-textarea"
            style={{
              minHeight: '520px',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              lineHeight: 1.6,
              background: '#030712',
            }}
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Direct edits will be saved as the active draft.
            </span>
            <button
              className="btn btn-primary btn-sm"
              onClick={handleSaveEdits}
              disabled={savingDirectEdits || editedContent === article?.content}
            >
              <Save size={14} />
              <span>{savingDirectEdits ? 'Saving...' : 'Save Direct Edits'}</span>
            </button>
          </div>
        </div>
      )}

      {activeTab === 'outline' && outline && (
        <div style={{ background: 'var(--bg-primary)', padding: '16px', borderRadius: '8px', maxHeight: '520px', overflowY: 'auto' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '12px', color: 'var(--primary)' }}>
            {outline.title}
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            {outline.summary}
          </p>

          <h4 style={{ fontSize: '14px', marginBottom: '8px' }}>Key Takeaways:</h4>
          <ul style={{ paddingLeft: '20px', marginBottom: '16px', fontSize: '13px' }}>
            {outline.key_takeaways?.map((item, idx) => (
              <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
            ))}
          </ul>

          <h4 style={{ fontSize: '14px', marginBottom: '8px' }}>Sections:</h4>
          {outline.sections?.map((sec, idx) => (
            <div key={idx} style={{ borderBottom: '1px solid var(--border)', paddingBottom: '8px', marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600 }}>
                <span>{sec.heading}</span>
                <span className="issue-timestamp">{sec.start_time} - {sec.end_time}</span>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>{sec.summary}</p>
            </div>
          ))}

          {outline.flagged_uncertainties?.length > 0 && (
            <div style={{ marginTop: '16px', background: 'var(--warning-bg)', padding: '12px', borderRadius: '6px' }}>
              <h4 style={{ fontSize: '13px', color: 'var(--warning)', marginBottom: '6px' }}>Flagged Uncertainties:</h4>
              <ul style={{ paddingLeft: '20px', fontSize: '12px' }}>
                {outline.flagged_uncertainties.map((u, i) => (
                  <li key={i}>{u}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <div style={{ maxHeight: '520px', overflowY: 'auto' }}>
          {versions.map((ver, idx) => (
            <div key={idx} style={{ background: 'var(--bg-primary)', padding: '14px', borderRadius: '8px', marginBottom: '12px', border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600, fontSize: '14px' }}>
                  Version {ver.version_number || idx + 1}
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {ver.timestamp ? new Date(ver.timestamp).toLocaleTimeString() : ''}
                </span>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                Title: {ver.title || 'Untitled Draft'}
              </p>
              <button
                className="btn btn-outline btn-sm"
                onClick={() => {
                  setEditedContent(ver.article?.markdown_article || ver.content || ver.markdown_article || '');
                  setActiveTab('preview');
                }}
              >
                Restore this draft to Editor
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
