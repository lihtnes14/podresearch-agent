import React, { useState } from 'react';
import { Youtube, Sparkles, Sliders } from 'lucide-react';

export default function InputForm({ onSubmit, loading }) {
  const [podcastUrl, setPodcastUrl] = useState('');
  const [videoTitle, setVideoTitle] = useState('');
  const [videoDescription, setVideoDescription] = useState('');
  const [articleStyle, setArticleStyle] = useState('technical, clear, and authoritative');
  const [targetAudience, setTargetAudience] = useState('Software engineers, AI developers, and tech leads');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!podcastUrl.trim()) return;
    onSubmit({
      podcast_url: podcastUrl.trim(),
      video_title: videoTitle.trim(),
      video_description: videoDescription.trim(),
      article_style: articleStyle.trim(),
      target_audience: targetAudience.trim(),
    });
  };

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '0 auto 24px auto' }}>
      <div className="card-title">
        <Youtube size={22} style={{ color: '#ef4444' }} />
        <span>Generate Article from YouTube Video</span>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">YouTube Video URL *</label>
          <input
            type="url"
            required
            className="form-input"
            placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/..."
            value={podcastUrl}
            onChange={(e) => setPodcastUrl(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Video Title (Optional)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Deep Dive into Agent Architectures"
              value={videoTitle}
              onChange={(e) => setVideoTitle(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Article Style</label>
            <select
              className="form-select"
              value={articleStyle}
              onChange={(e) => setArticleStyle(e.target.value)}
              disabled={loading}
            >
              <option value="technical, clear, and authoritative">Technical, Clear & Authoritative</option>
              <option value="educational and beginner-friendly">Educational & Step-by-Step</option>
              <option value="executive summary and business impact">Executive Summary & High-Level</option>
              <option value="deep dive tutorial with code">Developer Tutorial with Code</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <button
            type="button"
            className="btn btn-outline btn-sm"
            style={{ marginBottom: '12px' }}
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            <Sliders size={14} /> {showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'}
          </button>
        </div>

        {showAdvanced && (
          <div style={{ background: 'var(--bg-primary)', padding: '16px', borderRadius: '8px', marginBottom: '18px', border: '1px solid var(--border)' }}>
            <div className="form-group">
              <label className="form-label">Target Audience</label>
              <input
                type="text"
                className="form-input"
                placeholder="Target readers"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Video Description (Optional Context)</label>
              <textarea
                className="form-textarea"
                rows={3}
                placeholder="Paste the video description or any supplementary links"
                value={videoDescription}
                onChange={(e) => setVideoDescription(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', padding: '12px', fontSize: '15px' }}
          disabled={loading || !podcastUrl.trim()}
        >
          {loading ? (
            <>
              <div className="spinner" />
              <span>Running Autonomous Multi-Agent Pipeline...</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>Start Autonomous Pipeline (Agent 1 ➔ 2 ➔ 3)</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
