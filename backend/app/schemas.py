from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# =====================================================================
# AGENT 1 SCHEMAS: Content Analyst (Outline)
# =====================================================================

class SectionOutline(BaseModel):
    section_heading: str = Field(description="Clear, descriptive heading for this article section")
    key_points: List[str] = Field(description="Key concepts, insights, or steps in this section")
    relevant_timestamps: List[str] = Field(description="Original timestamps (e.g. ['01:15', '03:40']) relevant to this section")
    important_examples: List[str] = Field(default_factory=list, description="Concrete technical commands, code examples, or analogies")


class ArticleOutline(BaseModel):
    article_title: str = Field(description="Proposed publication title for the article")
    main_topic: str = Field(description="The core subject and purpose of the video")
    target_audience: str = Field(description="Intended audience (e.g., Software Engineers, DevOps Beginners)")
    key_takeaways: List[str] = Field(description="3-5 core takeaways that reader should learn")
    sections: List[SectionOutline] = Field(description="Ordered list of logical article sections grouped by meaning")
    uncertainties: List[str] = Field(default_factory=list, description="Ambiguous or unverified statements that require caution")


# =====================================================================
# AGENT 2 SCHEMAS: Article Writer (Drafting & Revision)
# =====================================================================

class ArticleOutput(BaseModel):
    title: str = Field(description="Final polished article title")
    markdown_article: str = Field(description="Complete article in Markdown format (including Title, Introduction, Sections with code blocks & timestamps, Uncertainties section, Conclusion, and YouTube link)")
    word_count: int = Field(default=0, description="Estimated word count of the generated article")


# =====================================================================
# AGENT 3 SCHEMAS: Editorial Reviewer (Quality Control)
# =====================================================================

class ReviewIssue(BaseModel):
    type: str = Field(description="Category of issue: 'unsupported_claim', 'technical_distortion', 'hallucinated_fact', or 'structure_issue'")
    section: str = Field(description="Section heading where the issue was detected")
    issue: str = Field(description="Detailed explanation of the issue")
    timestamp: Optional[str] = Field(default=None, description="Associated timestamp from transcript or article")
    severity: str = Field(description="Severity: 'high', 'medium', or 'low'")


class EditorialReviewOutput(BaseModel):
    approved: bool = Field(description="True if article is sufficiently accurate, complete, and grounded; False if revision is needed")
    overall_feedback: str = Field(description="Summary assessment of article quality and grounding")
    issues: List[ReviewIssue] = Field(default_factory=list, description="List of detected issues")
    missing_content: List[str] = Field(default_factory=list, description="Core concepts from outline missing in the article")
    timestamp_errors: List[str] = Field(default_factory=list, description="Invalid or unsupported timestamps")
    uncertainties_missing: List[str] = Field(default_factory=list, description="Uncertain facts omitted from the 'Uncertainties' section")
    writing_issues: List[str] = Field(default_factory=list, description="Repetitive, irrelevant, or poorly structured prose")
    revision_instructions: List[str] = Field(default_factory=list, description="Actionable revision instructions for Agent 2")


# =====================================================================
# HUMAN-IN-THE-LOOP & REST API SCHEMAS
# =====================================================================

class GenerateArticleRequest(BaseModel):
    podcast_url: str = Field(description="YouTube video URL")
    video_title: Optional[str] = Field(default=None, description="Optional custom video/article title")
    video_description: Optional[str] = Field(default="", description="Optional video description context")
    article_style: Optional[str] = Field(default="technical, clear, and authoritative", description="Desired writing style")
    target_audience: Optional[str] = Field(default=None, description="Target reader audience")


class HumanDecisionItem(BaseModel):
    issue_index: int = Field(default=0, description="Index of the issue in Agent 3's issue list")
    decision: str = Field(default="accept", description="'accept' (apply correction in revision) or 'reject' (human override to keep)")
    notes: Optional[str] = Field(default="", description="Optional human editor notes or override justification")


class HumanReviewRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Session ID to apply review feedback to")
    decisions: List[HumanDecisionItem] = Field(default_factory=list, description="Decisions per issue")
    custom_instructions: Optional[str] = Field(default="", description="Direct human revision instructions for Agent 2")
    direct_markdown_edits: Optional[str] = Field(default=None, description="Optional directly edited markdown content")
    selected_feedback: Optional[List[Any]] = Field(default=None, description="List of accepted feedback items")
    additional_instructions: Optional[str] = Field(default=None, description="Alternative field for custom instructions")
    direct_article_edits: Optional[str] = Field(default=None, description="Alternative field for direct markdown edits")


class HumanApproveRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Session ID to finalize and approve")
    final_article: Optional[str] = Field(default=None, description="Approved final article markdown")
    editor_notes: Optional[str] = Field(default="Approved by Human Editor-in-Chief.", description="Approval sign-off note")
    reviewer_notes: Optional[str] = Field(default=None, description="Optional reviewer feedback")


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "pod_research_2"
    version: str = "0.1.0"


# =====================================================================
# MEDIUM PUBLISHING SCHEMAS
# =====================================================================

class PublishMediumRequest(BaseModel):
    medium_token: Optional[str] = Field(default=None, description="Medium Integration Token. If not provided, falls back to server env.")
    publish_status: str = Field(default="draft", description="'draft', 'public', or 'unlisted'")
    tags: List[str] = Field(default_factory=lambda: ["podcast", "ai", "notes"], description="Tags (up to 5)")
    canonical_url: Optional[str] = Field(default=None, description="Original source link (e.g. YouTube video URL)")


class PublishMediumResponse(BaseModel):
    success: bool
    post_url: str
    post_id: str
    publish_status: str
    title: str
    author_name: str
    author_url: Optional[str] = None
    message: str


# =====================================================================
# DEV.TO PUBLISHING SCHEMAS
# =====================================================================

class PublishDevtoRequest(BaseModel):
    api_key: Optional[str] = Field(default=None, description="Dev.to API Key (from https://dev.to/settings/extensions)")
    published: bool = Field(default=False, description="False to create a draft, True to publish live immediately")
    tags: List[str] = Field(default_factory=lambda: ["podcast", "ai", "python"], description="Tags (up to 4)")
    canonical_url: Optional[str] = Field(default=None, description="Original YouTube video URL")


class PublishDevtoResponse(BaseModel):
    success: bool
    post_url: str
    post_id: int
    published: bool
    title: str
    author_name: str
    author_username: Optional[str] = None
    message: str
