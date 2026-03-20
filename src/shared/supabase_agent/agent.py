"""Supabase Agent 메인 클래스"""
import logging
import time
from pathlib import Path

from src.shared.ai_client import AIClient

from .prompts import (
    SUPABASE_AGENT_SYSTEM_PROMPT,
    build_command_prompt,
    classify_command,
)
from .schemas import AgentResponse, ToolType
from .tools import MigrationTool, ValidationTool

logger = logging.getLogger(__name__)


class SupabaseAgent:
    """Supabase 데이터베이스 전문가 Agent"""

    def __init__(
        self,
        supabase_client,
        ai_client: AIClient | None = None,
        dry_run: bool = False,
    ):
        """
        Args:
            supabase_client: Supabase 클라이언트
            ai_client: AI 클라이언트 (선택사항, 없으면 규칙 기반)
            dry_run: Dry-run 모드 (실제 실행하지 않음)
        """
        self.supabase = supabase_client
        self.ai_client = ai_client
        self.dry_run = dry_run

        # 도구 초기화
        self.migration_tool = MigrationTool(supabase_client)
        self.validation_tool = ValidationTool(supabase_client)

    async def execute(self, command: str) -> AgentResponse:
        """
        사용자 명령 실행

        Args:
            command: 자연어 명령

        Returns:
            AgentResponse: 실행 결과
        """
        start_time = time.time()

        try:
            if self.dry_run:
                return AgentResponse(
                    success=True,
                    message=f"[DRY-RUN] {command}\n(실제 실행하지 않음)",
                    execution_time=time.time() - start_time,
                )

            # 명령 분류
            cmd_type = classify_command(command)
            logger.info(f"명령 분류: {cmd_type} - {command}")

            # 규칙 기반 처리 (AI 없이도 작동)
            if "migration" in cmd_type:
                return await self._handle_migration(command, start_time)
            elif "validation" in cmd_type or "검증" in command or "확인" in command:
                return await self._handle_validation(command, start_time)
            elif "query" in cmd_type or "몇 개" in command or "개수" in command:
                return await self._handle_query(command, start_time)
            elif "schema" in cmd_type or "스키마" in command or "구조" in command:
                return await self._handle_schema(command, start_time)
            else:
                # AI 사용 (있는 경우)
                if self.ai_client:
                    return await self._handle_with_ai(command, start_time)
                else:
                    return AgentResponse(
                        success=False,
                        message=f"명령을 이해하지 못했습니다: {command}\n\n사용 가능한 명령:\n- Migration 007 실행해줘\n- conversation_sessions 테이블 확인해줘\n- 활성 세션 개수 알려줘",
                        execution_time=time.time() - start_time,
                    )

        except Exception as e:
            logger.error(f"명령 실행 실패: {e}")
            return AgentResponse(
                success=False,
                message=f"실행 중 오류 발생: {str(e)}",
                execution_time=time.time() - start_time,
            )

    async def _handle_migration(self, command: str, start_time: float) -> AgentResponse:
        """Migration 명령 처리"""
        # Migration 번호 추출 (예: "007", "7")
        import re

        numbers = re.findall(r"\d+", command)

        if not numbers:
            return AgentResponse(
                success=False,
                message="Migration 번호를 찾을 수 없습니다. 예: 'Migration 007 실행해줘'",
                execution_time=time.time() - start_time,
            )

        migration_id = numbers[0].zfill(3)  # "7" → "007"

        # Migration 파일 찾기
        migration_file = await self.migration_tool.find_migration(migration_id)

        if not migration_file:
            available = await self.migration_tool.list_migrations()
            return AgentResponse(
                success=False,
                message=f"Migration {migration_id}를 찾을 수 없습니다.\n\n사용 가능한 Migration:\n"
                + "\n".join([f"  - {Path(m).name}" for m in available]),
                execution_time=time.time() - start_time,
            )

        # Migration 실행
        result = await self.migration_tool.run_migration(migration_file)

        if result.success:
            message_parts = [
                f"✅ Migration {migration_id} 실행 완료!",
                f"\n파일: {result.migration_file}",
            ]

            if result.tables_created:
                message_parts.append(
                    f"\n생성된 테이블 ({len(result.tables_created)}개):"
                )
                for table in result.tables_created:
                    message_parts.append(f"  - {table}")

            if result.functions_created:
                message_parts.append(
                    f"\n생성된 함수 ({len(result.functions_created)}개):"
                )
                for func in result.functions_created:
                    message_parts.append(f"  - {func}()")

            message_parts.append(f"\n실행 시간: {result.execution_time:.2f}초")

            message_parts.append("\n\n다음 단계:")
            message_parts.append("  1. 검증: python verify_migration_007.py")
            message_parts.append("  2. FORCE_CONVERSATION_MOCK=false 설정")
            message_parts.append("  3. 서버 재시작")

            return AgentResponse(
                success=True,
                message="\n".join(message_parts),
                data={
                    "tables": result.tables_created,
                    "functions": result.functions_created,
                },
                tool_used=ToolType.MIGRATION,
                execution_time=time.time() - start_time,
            )
        else:
            return AgentResponse(
                success=False,
                message=f"❌ Migration {migration_id} 실행 실패\n\n오류:\n"
                + "\n".join([f"  - {err}" for err in result.errors]),
                execution_time=time.time() - start_time,
            )

    async def _handle_validation(
        self, command: str, start_time: float
    ) -> AgentResponse:
        """검증 명령 처리"""
        # 테이블 이름 추출
        keywords = ["conversation_sessions", "conversation_messages", "houses_data"]

        found_table = None
        for keyword in keywords:
            if keyword in command.lower():
                found_table = keyword
                break

        if found_table:
            result = await self.validation_tool.table_exists(found_table)

            if result.exists:
                message = f"✅ 테이블 '{found_table}'이(가) 존재합니다."
            else:
                message = f"❌ 테이블 '{found_table}'을(를) 찾을 수 없습니다."

            return AgentResponse(
                success=result.exists,
                message=message,
                data=result.model_dump(),
                tool_used=ToolType.VALIDATION,
                execution_time=time.time() - start_time,
            )

        # 함수 이름 추출
        func_keywords = [
            "get_or_create_conversation_session",
            "get_conversation_history",
            "save_conversation_message",
        ]

        found_func = None
        for keyword in func_keywords:
            if keyword in command.lower():
                found_func = keyword
                break

        if found_func:
            result = await self.validation_tool.function_exists(found_func)

            if result.exists:
                message = f"✅ 함수 '{found_func}()'이(가) 존재합니다."
            else:
                message = f"❌ 함수 '{found_func}()'을(를) 찾을 수 없습니다."

            return AgentResponse(
                success=result.exists,
                message=message,
                data=result.model_dump(),
                tool_used=ToolType.VALIDATION,
                execution_time=time.time() - start_time,
            )

        return AgentResponse(
            success=False,
            message="검증할 테이블이나 함수를 찾을 수 없습니다.\n예: 'conversation_sessions 테이블 확인해줘'",
            execution_time=time.time() - start_time,
        )

    async def _handle_query(self, command: str, start_time: float) -> AgentResponse:
        """데이터 조회 명령 처리"""
        # 간단한 개수 조회
        if "세션" in command and "개수" in command or "몇 개" in command:
            table = "conversation_sessions"

            # 조건 추출
            where = None
            if "활성" in command or "active" in command:
                where = "status=active"

            count = await self.validation_tool.count_rows(table, where)

            if count >= 0:
                condition_str = f" ({where})" if where else ""
                message = f"📊 {table} 테이블{condition_str}: {count}개"

                return AgentResponse(
                    success=True,
                    message=message,
                    data={"table": table, "count": count, "where": where},
                    tool_used=ToolType.QUERY,
                    execution_time=time.time() - start_time,
                )

        return AgentResponse(
            success=False,
            message="조회 명령을 이해하지 못했습니다.\n예: '활성 세션 개수 알려줘'",
            execution_time=time.time() - start_time,
        )

    async def _handle_schema(self, command: str, start_time: float) -> AgentResponse:
        """스키마 조회 명령 처리"""
        # TODO: 테이블 스키마 조회 구현
        return AgentResponse(
            success=False,
            message="스키마 조회 기능은 아직 구현되지 않았습니다.",
            execution_time=time.time() - start_time,
        )

    async def _handle_with_ai(self, command: str, start_time: float) -> AgentResponse:
        """AI를 사용한 명령 처리"""
        # TODO: AI를 사용한 고급 명령 처리
        prompt = build_command_prompt(command)
        # AI 호출 및 도구 선택/실행
        return AgentResponse(
            success=False,
            message="AI 기반 처리는 아직 구현되지 않았습니다.",
            execution_time=time.time() - start_time,
        )
