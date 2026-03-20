"""Migration 도구"""
import logging
import re
import time
from pathlib import Path

from ..schemas import MigrationResult

logger = logging.getLogger(__name__)


class MigrationTool:
    """Migration 실행 및 검증 도구"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def run_migration(self, file_path: str) -> MigrationResult:
        """
        Migration 파일 실행

        Args:
            file_path: Migration SQL 파일 경로

        Returns:
            MigrationResult: 실행 결과
        """
        start_time = time.time()

        try:
            # 파일 읽기
            migration_path = Path(file_path)
            if not migration_path.exists():
                return MigrationResult(
                    success=False,
                    migration_file=file_path,
                    errors=[f"파일을 찾을 수 없습니다: {file_path}"],
                    execution_time=time.time() - start_time,
                )

            sql_content = migration_path.read_text(encoding="utf-8")

            # SQL 실행 (Supabase Python SDK는 직접 SQL 실행을 지원하지 않음)
            # psycopg를 사용해야 함
            try:
                import psycopg
                from src.config import settings

                if not settings.database_url:
                    return MigrationResult(
                        success=False,
                        migration_file=file_path,
                        errors=["DATABASE_URL이 설정되지 않았습니다."],
                        execution_time=time.time() - start_time,
                    )

                with psycopg.connect(settings.database_url) as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql_content)
                        conn.commit()

                # 생성된 테이블 및 함수 추출
                tables = self._extract_tables(sql_content)
                functions = self._extract_functions(sql_content)

                execution_time = time.time() - start_time

                logger.info(
                    f"Migration {file_path} 실행 완료 ({execution_time:.2f}s)"
                )

                return MigrationResult(
                    success=True,
                    migration_file=file_path,
                    tables_created=tables,
                    functions_created=functions,
                    execution_time=execution_time,
                )

            except ImportError:
                return MigrationResult(
                    success=False,
                    migration_file=file_path,
                    errors=["psycopg 모듈이 설치되지 않았습니다. uv pip install psycopg"],
                    execution_time=time.time() - start_time,
                )
            except Exception as e:
                logger.error(f"Migration 실행 실패: {e}")
                return MigrationResult(
                    success=False,
                    migration_file=file_path,
                    errors=[str(e)],
                    execution_time=time.time() - start_time,
                )

        except Exception as e:
            logger.error(f"Migration 처리 실패: {e}")
            return MigrationResult(
                success=False,
                migration_file=file_path,
                errors=[f"처리 중 오류: {str(e)}"],
                execution_time=time.time() - start_time,
            )

    def _extract_tables(self, sql: str) -> list[str]:
        """SQL에서 생성된 테이블 이름 추출"""
        pattern = r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)"
        matches = re.findall(pattern, sql, re.IGNORECASE)
        return list(set(matches))

    def _extract_functions(self, sql: str) -> list[str]:
        """SQL에서 생성된 함수 이름 추출"""
        pattern = r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([a-zA-Z_][a-zA-Z0-9_]*)"
        matches = re.findall(pattern, sql, re.IGNORECASE)
        return list(set(matches))

    async def list_migrations(self, directory: str = "migrations") -> list[str]:
        """
        사용 가능한 Migration 파일 목록

        Args:
            directory: Migration 디렉토리 경로

        Returns:
            list[str]: Migration 파일 경로 목록
        """
        migration_dir = Path(directory)
        if not migration_dir.exists():
            return []

        sql_files = sorted(migration_dir.glob("*.sql"))
        return [str(f) for f in sql_files]

    async def find_migration(self, migration_id: str) -> str | None:
        """
        Migration ID로 파일 찾기

        Args:
            migration_id: Migration 번호 (예: "007")

        Returns:
            str | None: 찾은 파일 경로 또는 None
        """
        migrations = await self.list_migrations()

        # 패턴: 007_*.sql 또는 *007*.sql
        for migration in migrations:
            if migration_id in Path(migration).stem:
                return migration

        return None
