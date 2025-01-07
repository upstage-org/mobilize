from datetime import date
from pydantic import BaseModel, Field, conlist, constr, conint, confloat
from typing import List, Optional
from enum import Enum


class VoiceInput(BaseModel):
    voice: Optional[str] = None
    variant: str
    pitch: conint(ge=0, le=100)
    speed: conint(ge=0, le=300)
    amplitude: conint(ge=0, le=100)


class LinkInput(BaseModel):
    url: Optional[str] = None
    blank: bool
    effect: bool


class SaveMediaInput(BaseModel):
    id: Optional[int] = None
    name: constr(min_length=1)
    mediaType: constr(min_length=1)
    copyrightLevel: conint(ge=0)
    owner: Optional[str] = None
    stageIds: conlist(int)
    userIds: Optional[List[int]] = []
    tags: Optional[List[str]] = []
    w: confloat(ge=0)
    h: confloat(ge=0)
    note: Optional[str] = None
    urls: conlist(str)
    voice: Optional[VoiceInput] = None
    link: Optional[LinkInput] = None


class Asset(BaseModel):
    id: constr(min_length=1)


class SaveMediaPayload(BaseModel):
    asset: Asset


class MediaTableInput(BaseModel):
    def __init__(self, *args, **kwargs):
        print(kwargs)
        print(args)
        super().__init__(*args, **kwargs)

    page: Optional[conint(ge=1)] = Field(
        1, description="Page number, must be greater than or equal to 1"
    )
    limit: Optional[conint(ge=1)] = Field(
        10, description="Number of items per page, must be greater than or equal to 1"
    )
    sort: Optional[List[str]] = Field(
        None,
        description="Sort options, must be one of 'ASSET_TYPE_ID_ASC', 'ASSET_TYPE_ID_DESC', 'OWNER_ID_ASC', 'OWNER_ID_DESC', 'NAME_ASC', 'NAME_DESC', 'CREATED_ON_ASC', 'CREATED_ON_DESC'",
    )
    name: Optional[str] = Field(None, description="Name filter")
    mediaTypes: Optional[List[str]] = Field(None, description="List of media types")
    owners: Optional[List[str]] = Field(None, description="List of owners")
    stages: Optional[List[int]] = Field(None, description="List of stage IDs")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    createdBetween: Optional[List[date]] = Field(
        None, description="List of two dates representing the created date range"
    )


class AssetSortEnum(Enum):
    ASSET_TYPE_ID_ASC = "ASSET_TYPE_ID_ASC"
    ASSET_TYPE_ID_DESC = "ASSET_TYPE_ID_DESC"
    OWNER_ID_ASC = "OWNER_ID_ASC"
    OWNER_ID_DESC = "OWNER_ID_DESC"
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
    CREATED_ON_ASC = "CREATED_ON_ASC"
    CREATED_ON_DESC = "CREATED_ON_DESC"
