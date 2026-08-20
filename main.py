"""StarMoment web application entry point."""

import os
import json
from datetime import date
from pathlib import Path
import logging

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from llm.storywriter import get_cute_story
from spacephoto.photo import get_photo

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="StarMoment", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
logger = logging.getLogger(__name__)


class MomentRequest(BaseModel):
    date: date
    description: str = Field(min_length=3, max_length=500)


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((BASE_DIR / "static" / "index.html").read_text())


@app.post("/api/moment")
def create_moment(moment: MomentRequest) -> StreamingResponse:
    if moment.date > date.today():
        raise HTTPException(status_code=400, detail="Please choose today or a day in the past.")
    try:
        page_url, image_url, nasa_description = get_photo(moment.date)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="NASA's archive is unavailable right now.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    def stream():
        yield json.dumps({"type": "metadata", "image_url": image_url,
                          "page_url": page_url, "date": moment.date.isoformat()}) + "\n"
        try:
            for text in get_cute_story(
                moment.date, moment.description.strip(), image_url, nasa_description
            ):
                yield json.dumps({"type": "delta", "text": text}) + "\n"
            yield json.dumps({"type": "done"}) + "\n"
        except Exception as _e:
            logger.exception(f"An error occurred while generating the story: {_e}")
            yield json.dumps({"type": "error", "message":
                              "The stars went quiet for a moment. Please try again."}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson",
                             headers={"X-Content-Type-Options": "nosniff",
                                      "Cache-Control": "no-cache"})


def main() -> None:
    port = os.environ.get("PORT", 8000)
    uvicorn.run("main:app", host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
