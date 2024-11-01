from pydantic import BaseModel, computed_field


class Entry(BaseModel):
    country: str
    flag: str
    artist: str
    song: str
    votes: list[str]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def display_pts(self) -> list[int]:
        total = 0
        display_pts = []
        for vote in self.votes:
            try:
                total += int(float(vote))
            except ValueError:
                pass
            display_pts.append(total)
        return display_pts

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dq_statuses(self) -> list[bool]:
        is_dq = False
        dq_statuses = []
        for i in range(len(self.votes)):
            if self.votes[i].lower() == "dq":
                is_dq = True
            dq_statuses.append(is_dq)
        return dq_statuses

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sorting_pts(self) -> list[int]:
        sorting_pts = []
        for i in range(len(self.votes)):
            (
                sorting_pts.append(-1000)
                if self.dq_statuses[i]
                else sorting_pts.append(self.display_pts[i])
            )
        return sorting_pts

    def _validate_voter_num(self, voter_num: int) -> None:
        if voter_num < 0 or voter_num >= len(self.votes):
            raise IndexError(f"Voter number {voter_num} was invalid")

    def voter_count_after_voter(self, voter_num: int) -> int:
        self._validate_voter_num(voter_num)
        num_votes = 0
        for vote in self.votes[: voter_num + 1]:
            try:
                if int(float(vote)):
                    num_votes += 1
            except ValueError:
                continue
        return num_votes

    @computed_field  # type: ignore[prop-decorator]
    @property
    def num_voters(self) -> int:
        return self.voter_count_after_voter(len(self.votes) - 1)

    def pts_count_after_voter(self, points: int, voter_num: int) -> int:
        self._validate_voter_num(voter_num)
        count = 0
        for vote in self.votes[: voter_num + 1]:
            try:
                current_pts = int(float(vote))
                if current_pts == points:
                    count += 1
            except ValueError:
                continue
        return count

    @computed_field  # type: ignore[prop-decorator]
    @property
    def unique_pts(self) -> set[int]:
        scores: set[int] = set()
        for vote in self.votes:
            try:
                scores.add(int(float(vote)))
            except ValueError:
                continue
        return scores
