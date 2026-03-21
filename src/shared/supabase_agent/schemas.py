"""Supabase Agent 스키마"""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ToolType(str, Enum):
    """도구 타입"""

    MIGRATION = "migration"
    SCHEMA = "schema"
    RPC = "rpc"
    QUERY = "query"
    VALIDATION = "validation"


class AgentResponse(BaseModel):
    """Agent 응답"""

    success: bool
    message: str
    data: dict[str, Any] | None = None
    tool_used: ToolType | None = None
    execution_time: float | None = None


class MigrationResult(BaseModel):
    """Migration 실행 결과"""

    success: bool
    migration_file: str
    tables_created: list[str] = Field(default_factory=list)
    functions_created: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    execution_time: float


class TableSchema(BaseModel):
    """테이블 스키마 정보"""

    table_name: str
    columns: list[dict[str, Any]]
    indexes: list[str] = Field(default_factory=list)
    foreign_keys: list[dict[str, str]] = Field(default_factory=list)


class FunctionInfo(BaseModel):
    """RPC 함수 정보"""

    name: str
    parameters: list[dict[str, str]]
    return_type: str
    language: str = "plpgsql"


class ValidationResult(BaseModel):
    """검증 결과"""

    target: str
    exists: bool
    details: dict[str, Any] | None = None
    checked_at: datetime = Field(default_factory=datetime.now)


class QueryResult(BaseModel):
    """쿼리 실행 결과"""

    sql: str
    rows_affected: int | None = None
    data: list[dict[str, Any]] | None = None
    execution_time: float
