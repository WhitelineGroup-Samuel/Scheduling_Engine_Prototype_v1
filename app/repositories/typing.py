from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy import Select
from sqlalchemy.sql.elements import ColumnElement

# Generic model type for repositories
TModel = TypeVar("TModel")

# Common SQL typing aliases (loose but useful for signatures)
WhereClause = ColumnElement[bool]  # e.g., Model.col == value
OrderClause = Any  # ColumnElement[Any] | UnaryExpression | TextClause
SelectStmt = Select[Any]
