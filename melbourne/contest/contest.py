import xlrd
from pydantic import BaseModel, computed_field

from melbourne.contest.entry import Entry


class Contest(BaseModel):
    entries: list[Entry]
    voters: list[str]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def num_entries(self) -> int:
        return len(self.entries)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def num_voters(self) -> int:
        return len(self.voters)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def unique_pts(self) -> set[int]:
        scores: set[int] = set()
        for entry in self.entries:
            scores.update(entry.unique_pts)
        return scores

    def _validate_voter_num(self, voter_num: int) -> None:
        if voter_num < 0 or voter_num >= len(self.voters):
            raise IndexError(f"Voter number {voter_num} was invalid")

    def results_after_voter(self, voter_num: int) -> list[Entry]:
        self._validate_voter_num(voter_num)
        return sorted(
            self.entries,
            key=lambda x: [
                # Sort first by the number of points, and then the number of voters
                *[
                    -x.sorting_pts[voter_num],
                    -x.display_pts[voter_num],
                    -x.voter_count_after_voter(voter_num),
                ],
                # Sort by the number of times each set of points was received
                *[
                    -x.pts_count_after_voter(p, voter_num)
                    for p in sorted(self.unique_pts, reverse=True)
                ],
                # Sort by the entry's country, artist, and song
                *[x.country, x.artist, x.song],
            ],
        )

    @staticmethod
    def _parse_excel_to_contest(
        excel: xlrd.Book, contains_count_col: bool
    ) -> "Contest":
        sheet = excel.sheet_by_index(0)
        if sheet.ncols < 7:
            raise ValueError("Excel sheet does not have enough columns")
        if sheet.nrows < 2:
            raise ValueError("Excel sheet does not have enough rows")

        # If the Excel file contains the "Count" column after the "Total" column,
        # start looking for votes one additional column afterwards
        start_of_votes_col = 7 if contains_count_col else 6
        voters = [str(cell.value).strip() for cell in sheet.row(0)[start_of_votes_col:]]

        entries = []
        for row in [row for row in sheet.get_rows()][1:]:
            country = str(row[1].value).strip()
            flag = str(row[2].value).strip()
            artist = str(row[3].value).strip()
            song = str(row[4].value).strip()
            votes = [str(cell.value).strip() for cell in row[start_of_votes_col:]]

            # We want to stop reading once we see a row without these required fields
            if not (country and artist and song):
                break

            entries.append(
                Entry(country=country, flag=flag, artist=artist, song=song, votes=votes)
            )

        return Contest(entries=entries, voters=voters)

    @staticmethod
    def from_file(file_path: str, contains_count_col: bool) -> "Contest":
        excel = xlrd.open_workbook(filename=file_path)
        return Contest._parse_excel_to_contest(excel, contains_count_col)

    @staticmethod
    def from_bytes(file_contents: bytes, contains_count_col: bool) -> "Contest":
        excel = xlrd.open_workbook(file_contents=file_contents)
        return Contest._parse_excel_to_contest(excel, contains_count_col)
