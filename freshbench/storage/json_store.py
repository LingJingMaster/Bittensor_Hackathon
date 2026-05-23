from __future__ import annotations

from pathlib import Path

from freshbench.schemas import AssetSubmission, ScoringReport

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


class JsonStore:
    """File-backed JSON store for submissions and scoring reports.

    Layout under ``base_dir``::

        submissions/{task_id}.json
        reports/{asset_id}.json
    """

    def __init__(self, base_dir: Path | str | None = None) -> None:
        base = Path(base_dir) if base_dir is not None else DEFAULT_DATA_DIR
        self.base_dir = base
        self.submissions_dir = base / "submissions"
        self.reports_dir = base / "reports"

    def save_submission(self, submission: AssetSubmission) -> str:
        self.submissions_dir.mkdir(parents=True, exist_ok=True)
        path = self.submissions_dir / f"{submission.task_id}.json"
        path.write_text(submission.model_dump_json(indent=2), encoding="utf-8")
        return str(path)

    def save_report(self, report: ScoringReport) -> str:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        path = self.reports_dir / f"{report.asset_id}.json"
        path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return str(path)

    def load_report(self, asset_id: str) -> ScoringReport | None:
        path = self.reports_dir / f"{asset_id}.json"
        if not path.exists():
            return None
        return ScoringReport.model_validate_json(path.read_text(encoding="utf-8"))

    def list_reports(self) -> list[ScoringReport]:
        if not self.reports_dir.exists():
            return []
        reports: list[ScoringReport] = []
        for path in sorted(self.reports_dir.glob("*.json")):
            reports.append(
                ScoringReport.model_validate_json(path.read_text(encoding="utf-8"))
            )
        return reports


_default_store = JsonStore()


def save_submission(submission: AssetSubmission) -> str:
    return _default_store.save_submission(submission)


def save_report(report: ScoringReport) -> str:
    return _default_store.save_report(report)


def load_report(asset_id: str) -> ScoringReport | None:
    return _default_store.load_report(asset_id)


def list_reports() -> list[ScoringReport]:
    return _default_store.list_reports()
