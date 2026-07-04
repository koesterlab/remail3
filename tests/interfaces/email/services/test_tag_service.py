from remail.interfaces.email.services.tag_service import DEFAULT_TAGS, TagService


def test_get_all_tags_seeds_defaults(session):
    service = TagService()

    tags = service.get_all_tags(session=session)

    assert {tag.name for tag in tags} == {name for name, _description in DEFAULT_TAGS}


def test_create_and_delete_tag(session):
    service = TagService()

    tag = service.create_tag("Project", "Project emails", session=session)

    assert tag.name == "Project"
    assert any(saved.name == "Project" for saved in service.get_all_tags(session=session))

    service.delete_tag(tag.id, session=session)

    assert all(saved.name != "Project" for saved in service.get_all_tags(session=session))
