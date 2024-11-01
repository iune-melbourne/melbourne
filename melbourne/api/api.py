import logging

from fastapi import FastAPI, Form, UploadFile

from melbourne.contest.contest import Contest
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

app = FastAPI()


class Settings(BaseSettings):
    working_dir: str
    fonts_dir: str
    flags_dir: str

    model_config = SettingsConfigDict(env_file=".env")


@app.post("/api/contest")
async def parse_contest(
    contest_file: UploadFile, contains_count_col: bool = Form(False)
) -> Contest:
    contest = Contest.from_bytes(contest_file.file.read(), contains_count_col)
    return contest
