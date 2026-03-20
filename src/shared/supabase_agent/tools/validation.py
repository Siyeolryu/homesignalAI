"""검증 도구"""
import logging
from datetime import datetime

from ..schemas import ValidationResult

logger = logging.getLogger(__name__)


class ValidationTool:
    """테이블, 함수 등 존재 여부 검증 도구"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def table_exists(self, table_name: str) -> ValidationResult:
        """
        테이블 존재 확인

        Args:
            table_name: 테이블 이름

        Returns:
            ValidationResult: 검증 결과
        """
        try:
            # SELECT * LIMIT 0으로 테이블 접근 가능 여부 확인
            result = self.supabase.table(table_name).select("*").limit(0).execute()

            return ValidationResult(
                target=f"table:{table_name}",
                exists=True,
                details={"method": "supabase_select"},
            )
        except Exception as e:
            error_msg = str(e).lower()

            # "relation does not exist" 에러면 테이블 없음
            if "does not exist" in error_msg or "not found" in error_msg:
                return ValidationResult(
                    target=f"table:{table_name}",
                    exists=False,
                    details={"error": str(e)},
                )

            # 다른 에러 (권한 등)
            logger.warning(f"테이블 {table_name} 확인 중 에러: {e}")
            return ValidationResult(
                target=f"table:{table_name}",
                exists=False,
                details={"error": str(e), "ambiguous": True},
            )

    async def function_exists(self, function_name: str) -> ValidationResult:
        """
        RPC 함수 존재 확인

        Args:
            function_name: 함수 이름

        Returns:
            ValidationResult: 검증 결과
        """
        try:
            # 빈 파라미터로 함수 호출 시도 (에러 메시지로 존재 여부 판단)
            try:
                self.supabase.rpc(function_name, {}).execute()
                # 성공하면 존재함
                return ValidationResult(
                    target=f"function:{function_name}",
                    exists=True,
                    details={"method": "rpc_call"},
                )
            except Exception as e:
                error_msg = str(e).lower()

                # "could not find the function" 에러면 함수 없음
                if "could not find" in error_msg or "does not exist" in error_msg:
                    return ValidationResult(
                        target=f"function:{function_name}",
                        exists=False,
                        details={"error": str(e)},
                    )

                # 파라미터 에러나 다른 실행 에러면 함수는 존재하는 것
                if "parameter" in error_msg or "argument" in error_msg:
                    return ValidationResult(
                        target=f"function:{function_name}",
                        exists=True,
                        details={"error": "파라미터 필요", "method": "rpc_call"},
                    )

                # 기타 에러
                return ValidationResult(
                    target=f"function:{function_name}",
                    exists=False,
                    details={"error": str(e), "ambiguous": True},
                )

        except Exception as e:
            logger.error(f"함수 {function_name} 확인 중 예외: {e}")
            return ValidationResult(
                target=f"function:{function_name}",
                exists=False,
                details={"error": str(e)},
            )

    async def validate_migration(
        self, expected_tables: list[str], expected_functions: list[str]
    ) -> dict[str, bool]:
        """
        Migration 결과 검증

        Args:
            expected_tables: 예상되는 테이블 목록
            expected_functions: 예상되는 함수 목록

        Returns:
            dict[str, bool]: 각 항목별 검증 결과
        """
        results = {}

        # 테이블 검증
        for table in expected_tables:
            result = await self.table_exists(table)
            results[f"table:{table}"] = result.exists

        # 함수 검증
        for func in expected_functions:
            result = await self.function_exists(func)
            results[f"function:{func}"] = result.exists

        return results

    async def count_rows(self, table_name: str, where: str | None = None) -> int:
        """
        테이블 레코드 개수 조회

        Args:
            table_name: 테이블 이름
            where: WHERE 조건 (선택사항)

        Returns:
            int: 레코드 개수
        """
        try:
            query = self.supabase.table(table_name).select("*", count="exact")

            # WHERE 조건이 있으면 적용 (간단한 경우만)
            # 예: "status=active" → eq("status", "active")
            if where:
                # 간단한 파싱 (=, >, < 등)
                if "=" in where:
                    col, val = where.split("=", 1)
                    query = query.eq(col.strip(), val.strip().strip("'\""))

            result = query.execute()

            # count 속성 확인
            if hasattr(result, "count") and result.count is not None:
                return result.count

            # count가 없으면 len(data) 사용
            if result.data:
                return len(result.data)

            return 0

        except Exception as e:
            logger.error(f"테이블 {table_name} 레코드 개수 조회 실패: {e}")
            return -1
