from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RunExport(Base):
    """
    ERD TABLE: run_exports
    PURPOSE: Records of exported artifacts per run.

    Columns:
      - export_id SERIAL PK
      - run_id INTEGER NOT NULL FK -> scheduling_runs(run_id)
      - export_type TEXT NOT NULL  // CHECK: 'CSV','PDF','ZIP','XLSX'
      - file_path TEXT NOT NULL    [AK]
      - created_at TIMESTAMPTZ NULLABLE [default NOW()]

    AK / Indexes:
      - UNIQUE (run_id, export_type) -> uq_run_exports_run_type
      - UNIQUE (file_path)           -> uq_run_exports_file_path
      - INDEX  (run_id)              -> idx_run_exports_run
    """

    __tablename__ = "run_exports"

    export_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("scheduling_runs.run_id"), nullable=False)
    export_type: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    __table_args__ = (
        UniqueConstraint("run_id", "export_type", name="uq_run_exports_run_type"),
        UniqueConstraint("file_path", name="uq_run_exports_file_path"),
        CheckConstraint(
            "export_type IN ('CSV','PDF','ZIP','XLSX')",
            name="chk_run_exports_export_type",
        ),
        Index("idx_run_exports_run", "run_id"),
    )

    # Relationships
    run = relationship("SchedulingRun", back_populates="exports")

    def __repr__(self) -> str:
        return f"<RunExport id={self.export_id} run_id={self.run_id} type={self.export_type!r}>"
