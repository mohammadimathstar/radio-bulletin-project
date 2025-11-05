from typing import List, Optional, Literal
from datetime import date
from pydantic import BaseModel, Field


# ---------- Base Classes ----------

class BaseEntity(BaseModel):
    id: str = Field(..., description="Unique ID for this entity within the bulletin (entity_type + number).")
    name: str = Field(..., description="Exact name as mentioned in the text.")
    description: Optional[str] = Field(None, description="Short summary or appositive phrase from the text (in English).")
    text_span: str = Field(..., description="Text snippet mentioning this entity, exactly as in transcript.")
    context_sentence: Optional[str] = Field(
        None,
        description=(
            "Return the exact sentence from the transcript that contains the entity. "
            "Do not add quotes, brackets, or any special formatting. "
            "Remove line breaks, tabs, or unusual symbols. "
            "Return plain UTF-8 text only. If not available, return null."
        )
    )


# ---------- Entities ----------

class Person(BaseEntity):
    entity_type: Literal["person"] = "person"
    inferred_full_name: str = Field(..., description="Inferred full name based on context and time period, without any title.")
    nationality: Optional[str] = Field(None, description="Country of citizenship or origin if stated (in English).")
    occupation: Optional[List[str]] = Field(None, description="Occupations, roles, or titles mentioned in text (in English).")
    gender: Optional[str] = Field(None, description="Gender if mentioned.")


class Organization(BaseEntity):
    entity_type: Literal["organization"] = "organization"
    official_name: str = Field(..., description="Official full name of the organization (in English).")
    org_type: Optional[str] = Field(None, description="Type of organization (e.g., 'company', 'political party') (in English).")
    location: Optional[str] = Field(None, description="The location that the organization is located in (in English).")

class Location(BaseEntity):
    entity_type: Literal["location"] = "location"
    location_type: Optional[str] = Field(None, description="Type of location (e.g., 'city', 'country', 'region') (in English).")
    country: Optional[str] = Field(None, description="If this location is inside another country, name that country (in English).")


class Publication(BaseModel):
    id: str = Field(..., description="ID of the publication entity.")
    title: str = Field(..., description="Title of the publication.")
    text_span: str = Field(..., description="Text snippet mentioning the publication.")
    entity_type: Literal["publication"] = "publication"
    date_time: Optional[date] = Field(None, description="Publication date if provided.")
    publisher: Optional[str] = Field(None, description="Publisher of the publication.")
    type: Optional[str] = Field(None, description="Type of publication (e.g., 'newspaper', 'journal').")


class Event(BaseEntity):
    entity_type: Literal["event"] = "event"
    start_date: Optional[date] = Field(None, description="Start date if mentioned.")
    end_date: Optional[date] = Field(None, description="End date if mentioned.")
    location: Optional[str] = Field(None, description="Location name as mentioned (in English).")
    participants: Optional[List[str]] = Field(None, description="IDs of people/organizations involved in the event.")
    event_type: Optional[str] = Field(None, description="Type of event (e.g., 'election', 'speech', 'conflict') (in English).")


class Artifact(BaseEntity):
    entity_type: Literal["artifact"] = "artifact"
    artifact_type: Optional[str] = Field(None, description="Type of artifact (e.g., 'treaty', 'law', 'ship') (in English).")
    creation_date: Optional[date] = Field(None, description="Creation date if explicitly mentioned.")


# ---------- Relations ----------

class Relation(BaseModel):
    source_id: str = Field(..., description="ID of the source entity.")
    target_id: str = Field(..., description="ID of the target entity.")
    relation_type: Literal[
        "member_of",
        "located_in",
        "participated_in",
        "occurred_at",
        "gave_speech",
        "authored",
        "signed",
        "produced",
        "published",
        "part_of",
        "caused",
        "opposed",
        "supported",
        "reported_on",
        "affected",
        "succeeded_by",
        "preceded_by",
        "supervised_by"
    ] = Field(..., description="Relation type between entities.")
    certainty: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0.")


# ---------- Top-level container ----------

class BulletinExtraction(BaseModel):
    transcript: str = Field(..., description="The denoised transcript of the radio bulletin.")
    bulletin_topic: str = Field(..., description="A few words describing the topic of the bulletin.")
    bulletin_summary: str = Field(..., description="A short description summarizing the bulletin.")
    
    people: List[Person] = Field(default_factory=list)
    organizations: List[Organization] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    publications: List[Publication] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    artifacts: List[Artifact] = Field(default_factory=list)
    relations: List[Relation] = Field(default_factory=list)
    
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence in extraction.")
    # ocr_span: Optional[str] = Field(None, description="Original OCR text span used for debugging.")

    model_config = {"extra": "allow"}  # Accept unknown keys without failing