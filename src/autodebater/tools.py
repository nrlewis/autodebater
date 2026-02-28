"""
LangChain tools available to tool-enabled debaters.
"""

import logging

logger = logging.getLogger(__name__)


def get_default_tools() -> list:
    """Return a list of default LangChain tools for debaters."""
    tools = []
    try:
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper

        tools.append(WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()))
    except Exception as exc:  # pragma: no cover
        logger.warning("WikipediaQueryRun unavailable: %s", exc)

    try:
        from langchain_community.tools import DuckDuckGoSearchRun

        tools.append(DuckDuckGoSearchRun())
    except Exception as exc:  # pragma: no cover
        logger.warning("DuckDuckGoSearchRun unavailable: %s", exc)

    return tools
