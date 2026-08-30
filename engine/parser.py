from typing import Dict, Any, List, Optional
from models.schema import (
    ProfileResponse, Experience, Education, Certification, Language, DateRange
)

def _parse_date(date_obj: Optional[Dict[str, Any]]) -> Optional[str]:
    if not isinstance(date_obj, dict):
        return None
    year = date_obj.get("year")
    month = date_obj.get("month", 1)
    day = date_obj.get("day", 1)
    if year:
        return f"{year:04d}-{month:02d}-{day:02d}"
    return None

def parse_voyager_response(raw_json: Dict[str, Any], target_slug: str) -> ProfileResponse:
    included = raw_json.get("included") or []
    
    profile_entity: Optional[Dict[str, Any]] = None
    experiences: List[Experience] = []
    educations: List[Education] = []
    skills: List[str] = []
    certifications: List[Certification] = []
    languages: List[Language] = []
    
    for item in included:
        if not isinstance(item, dict):
            continue
            
        entity_type = item.get("$type", "")
        
        # Profile Root Entity
        if "com.linkedin.voyager.dash.identity.profile.Profile" in entity_type:
            if item.get("publicIdentifier") == target_slug or profile_entity is None:
                profile_entity = item
                
        # Work Positions
        elif "com.linkedin.voyager.dash.identity.profile.Position" in entity_type:
            dr = item.get("dateRange") or {}
            experiences.append(Experience(
                title=item.get("title"),
                company_name=item.get("companyName"),
                location=item.get("locationName"),
                description=item.get("description"),
                date_range=DateRange(
                    starts_at=_parse_date(dr.get("start")),
                    ends_at=_parse_date(dr.get("end"))
                )
            ))
            
        # Education History
        elif "com.linkedin.voyager.dash.identity.profile.Education" in entity_type:
            dr = item.get("dateRange") or {}
            educations.append(Education(
                school_name=item.get("schoolName"),
                degree_name=item.get("degreeName"),
                field_of_study=item.get("fieldOfStudy"),
                date_range=DateRange(
                    starts_at=_parse_date(dr.get("start")),
                    ends_at=_parse_date(dr.get("end"))
                )
            ))
            
        # Skills
        elif "com.linkedin.voyager.dash.identity.profile.Skill" in entity_type:
            if item.get("name"):
                skills.append(item["name"])
                
        # Certifications
        elif "com.linkedin.voyager.dash.identity.profile.Certification" in entity_type:
            certifications.append(Certification(
                name=item.get("name"),
                authority=item.get("authority"),
                license_number=item.get("licenseNumber"),
                url=item.get("url")
            ))
            
        # Languages
        elif "com.linkedin.voyager.dash.identity.profile.Language" in entity_type:
            languages.append(Language(
                name=item.get("name"),
                proficiency=item.get("proficiency")
            ))

    # Resolve high-resolution profile picture
    image_url: Optional[str] = None
    if profile_entity and isinstance(profile_entity.get("profilePicture"), dict):
        pic_data = profile_entity["profilePicture"]
        pic_ref = pic_data.get("displayImageReferenceResolutionGroup") or {}
        root_url = pic_ref.get("rootUrl", "")
        artifacts = pic_ref.get("artifacts") or []
        if root_url and artifacts:
            max_artifact = max(artifacts, key=lambda a: a.get("width", 0) if isinstance(a, dict) else 0)
            if isinstance(max_artifact, dict):
                image_url = root_url + max_artifact.get("fileIdentifyingUrlPathSegment", "")

    return ProfileResponse(
        public_identifier=target_slug,
        first_name=profile_entity.get("firstName") if profile_entity else None,
        last_name=profile_entity.get("lastName") if profile_entity else None,
        headline=profile_entity.get("headline") if profile_entity else None,
        location=profile_entity.get("locationName") if profile_entity else None,
        about=profile_entity.get("summary") if profile_entity else None,
        profile_picture_url=image_url,
        experiences=experiences,
        educations=educations,
        skills=skills,
        certifications=certifications,
        languages=languages
    )
