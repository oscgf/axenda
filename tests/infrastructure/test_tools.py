
from axenda.infrastructure.llm.tools import ALL_TOOLS, SEARCH_EVENTS_TOOL


class TestTools:
    def test_search_events_tool_structure(self) -> None:
        tool = SEARCH_EVENTS_TOOL
        assert tool["type"] == "function"
        func = tool["function"]
        assert func["name"] == "search_events"
        assert "city" in func["parameters"]["properties"]
        assert "city" in func["parameters"]["required"]
        assert "event_type" in func["parameters"]["properties"]
        assert "genre" in func["parameters"]["properties"]

    def test_search_events_enum(self) -> None:
        enum = SEARCH_EVENTS_TOOL["function"]["parameters"]["properties"]["event_type"]["enum"]
        assert "Música" in enum
        assert "Teatro" in enum
        assert "Otros" in enum

    def test_all_tools_list(self) -> None:
        assert len(ALL_TOOLS) == 3
        names = [t["function"]["name"] for t in ALL_TOOLS]
        assert "search_events" in names
        assert "get_event_details" in names
        assert "list_venues" in names
