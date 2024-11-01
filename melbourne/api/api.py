import logging

from fastapi import FastAPI, Form, UploadFile
from pydantic import BaseModel

from melbourne.contest.contest import Contest
from melbourne.contest.entry import Entry

logger = logging.getLogger(__name__)

app = FastAPI()


class ParseContestResponse(BaseModel):
    entries: list[Entry]
    voters: list[str]


@app.post("/api/contest")
async def parse_contest(
    contest_file: UploadFile, contains_count_col: bool = Form(False)
) -> Contest:
    contest = Contest.from_bytes(contest_file.file.read(), contains_count_col)
    return contest
