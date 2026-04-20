import os
import logging

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INK_API_URL = os.environ.get("INK_API_URL", "https://pdf-annotator-ink.fly.dev").rstrip("/")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

mcp = FastMCP("ink-mcp-server", host="0.0.0.0", stateless_http=True)


def _check_health() -> None:
    try:
        r = httpx.get(f"{INK_API_URL}/healthz", timeout=10)
        if r.status_code == 200:
            logger.info("Ink API healthy: %s", r.json())
        else:
            logger.warning("Ink API /healthz returned %s", r.status_code)
    except Exception as exc:
        logger.warning("Ink API unreachable: %s", exc)


@mcp.tool(
    description=(
        "Annotate a PDF with AI-powered highlights, margin notes, and symbols. "
        "Returns the annotated PDF and annotation statistics."
    )
)
def annotate_pdf(
    pdf_b64: str,
    document_title: str | None = None,
    anthropic_api_key: str | None = None,
) -> dict:
    """
    pdf_b64: Base64-encoded PDF bytes
    document_title: Optional title of the document
    anthropic_api_key: Override the server's Anthropic API key
    """
    body: dict = {"pdf_b64": pdf_b64}
    if document_title:
        body["document_title"] = document_title

    headers: dict = {}
    key = anthropic_api_key or ANTHROPIC_API_KEY
    if key:
        headers["x-anthropic-api-key"] = key

    try:
        with httpx.Client(timeout=300) as client:
            response = client.post(
                f"{INK_API_URL}/annotate",
                json=body,
                headers=headers,
            )
    except httpx.RequestError as exc:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Network error: {exc}"))

    if not response.is_success:
        try:
            msg = response.json().get("error", response.text)
        except Exception:
            msg = response.text
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Ink API error {response.status_code}: {msg}"))

    data = response.json()
    return {"pdf_b64": data["pdf_b64"], "stats": data["stats"]}


if __name__ == "__main__":
    _check_health()
    mcp.run(transport="streamable-http")
