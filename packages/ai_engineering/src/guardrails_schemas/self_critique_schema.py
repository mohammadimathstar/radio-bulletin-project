from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, confloat
from guardrail.schemas import (
    Person,
    Organization,
    Location,
    Publication,
    Event,
    Artifact,
    Relation,
    BulletinExtraction,
)

class CritiqueIssue(BaseModel):
    """A single issue identified in the extraction."""
    issue_type: str = Field(
        ...,
        description="Type of issue, e.g., 'missing_entity', 'incorrect_relation', 'wrong_field_value', etc."
    )
    description: str = Field(
        ...,
        description="Short explanation of what is wrong or missing."
    )
    entity_id: Optional[str] = Field(
        None,
        description="Entity ID if the issue concerns a specific entity."
    )
    field: Optional[str] = Field(
        None,
        description="Specific field (e.g., 'text_span', 'event_type') if applicable."
    )
    severity: Optional[str] = Field(
        "moderate",
        description="Severity level: 'minor', 'moderate', or 'critical'."
    )


class SelfCritiqueOutput(BaseModel):
    """
    Schema for the self-critique stage.
    The LLM reviews a previous extraction and returns structured feedback.
    """
    valid: bool = Field(
        ...,
        description="True if the extraction is largely correct; false if major issues exist."
    )
    confidence: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description="Model's confidence in its critique (0–1)."
    )
    comments: str = Field(
        ...,
        description="High-level summary of the critique findings."
    )

    # List of detailed problems found
    issues: Optional[List[CritiqueIssue]] = Field(
        default_factory=list,
        description="List of specific problems in entities, relations, or metadata."
    )

    # New or corrected structured data
    suggested_new_people: Optional[List[Person]] = Field(default_factory=list)
    suggested_new_organizations: Optional[List[Organization]] = Field(default_factory=list)
    suggested_new_locations: Optional[List[Location]] = Field(default_factory=list)
    suggested_new_publications: Optional[List[Publication]] = Field(default_factory=list)
    suggested_new_events: Optional[List[Event]] = Field(default_factory=list)
    suggested_new_artifacts: Optional[List[Artifact]] = Field(default_factory=list)
    suggested_new_relations: Optional[List[Relation]] = Field(default_factory=list)

    # Optionally propose a corrected extraction JSON
    suggested_corrections: Optional[BulletinExtraction] = Field(
        None,
        description="Optional corrected full extraction object following BulletinExtraction schema."
    )

    model_config = {"extra": "allow"}  # Allow additional fields if needed
