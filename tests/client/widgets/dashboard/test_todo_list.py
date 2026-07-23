from types import SimpleNamespace
from unittest.mock import Mock, patch

from remail.client.widgets.dashboard.todo_list import TodoList


def _state_with_tags() -> SimpleNamespace:
    thread_controller = Mock()
    thread_controller.get_most_urgent_threads.return_value = []

    tag_controller = Mock()
    tag_controller.get_all_tags.return_value = [
        SimpleNamespace(id=7, name="Work"),
        SimpleNamespace(id=9, name="Personal"),
    ]

    return SimpleNamespace(
        thread_controller=thread_controller,
        tag_controller=tag_controller,
        register_observer=Mock(),
    )


def test_todo_list_builds_tag_filter_options() -> None:
    state = _state_with_tags()

    todo_list = TodoList(state)

    assert [option.key for option in todo_list.tag_filter.options] == ["all", "7", "9"]
    assert [option.text for option in todo_list.tag_filter.options] == [
        "All tags",
        "Work",
        "Personal",
    ]


def test_todo_list_reloads_for_selected_tag_and_all_tags() -> None:
    state = _state_with_tags()
    todo_list = TodoList(state)

    with patch.object(todo_list, "update") as update:
        todo_list._on_tag_selected(SimpleNamespace(control=SimpleNamespace(value="7")))

        state.thread_controller.get_most_urgent_threads.assert_called_with(
            count=5,
            tag_id=7,
        )
        assert todo_list.count_text.value == "0 emails to answer"
        update.assert_called_once_with()

        todo_list._on_tag_selected(SimpleNamespace(control=SimpleNamespace(value="all")))

        state.thread_controller.get_most_urgent_threads.assert_called_with(
            count=5,
            tag_id=None,
        )
        assert update.call_count == 2


def test_todo_list_refreshes_options_when_tags_change() -> None:
    state = _state_with_tags()
    todo_list = TodoList(state)
    tags_changed_callback = state.register_observer.call_args.args[1]

    state.tag_controller.get_all_tags.return_value = [
        SimpleNamespace(id=9, name="Personal"),
        SimpleNamespace(id=11, name="Finance"),
    ]
    todo_list.tag_filter.value = "7"

    with patch.object(todo_list, "update") as update:
        tags_changed_callback(1)

    assert [option.key for option in todo_list.tag_filter.options] == ["all", "9", "11"]
    assert todo_list.tag_filter.value == "all"
    state.thread_controller.get_most_urgent_threads.assert_called_with(
        count=5,
        tag_id=None,
    )
    update.assert_called_once_with()


def test_todo_list_refreshes_current_filter_when_tag_assignments_change() -> None:
    state = _state_with_tags()
    todo_list = TodoList(state)
    tags_changed_callback = state.register_observer.call_args.args[1]
    todo_list.tag_filter.value = "7"

    with patch.object(todo_list, "update") as update:
        tags_changed_callback(1)

    state.thread_controller.get_most_urgent_threads.assert_called_with(
        count=5,
        tag_id=7,
    )
    update.assert_called_once_with()


def test_todo_list_shows_empty_state_when_no_threads_match() -> None:
    state = _state_with_tags()

    todo_list = TodoList(state)

    assert len(todo_list.items_column.controls) == 1
    assert todo_list.items_column.controls[0].value == ("No To Do emails match this tag.")
