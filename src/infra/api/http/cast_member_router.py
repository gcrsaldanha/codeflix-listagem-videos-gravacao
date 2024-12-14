from typing import Any

from fastapi import Depends, Query, APIRouter

from src.application.list_cast_member import CastMemberSortableFields, ListCastMember, ListCastMemberInput
from src.application.listing import ListOutput
from src.domain.cast_member import CastMember
from src.infra.api.http.dependencies import common_parameters, get_cast_member_repository
from src.infra.elasticsearch.elasticsearch_cast_member_repository import ElasticsearchCastMemberRepository

router = APIRouter()


@router.get("/", response_model=ListOutput[CastMember])
def list_cast_members(
    repository: ElasticsearchCastMemberRepository = Depends(get_cast_member_repository),
    sort: CastMemberSortableFields = Query(CastMemberSortableFields.NAME, description="Field to sort by"),
    common: dict[str, Any] = Depends(common_parameters),
) -> ListOutput[CastMember]:
    return ListCastMember(repository=repository).execute(
        ListCastMemberInput(
            search=common["search"],
            page=common["page"],
            per_page=common["per_page"],
            sort=sort,
            direction=common["direction"],
        )
    )
