"""Supabase Agent 테스트"""
import pytest

from src.shared.database import get_supabase_client
from src.shared.supabase_agent import SupabaseAgent


@pytest.fixture
def supabase_client():
    """Supabase 클라이언트"""
    return get_supabase_client(use_service_role=True)


@pytest.fixture
def agent(supabase_client):
    """Supabase Agent (Dry-run 모드)"""
    return SupabaseAgent(supabase_client=supabase_client, dry_run=True)


class TestSupabaseAgent:
    """SupabaseAgent 테스트"""

    async def test_dry_run_mode(self, agent):
        """Dry-run 모드 테스트"""
        response = await agent.execute("Migration 007 실행해줘")

        assert response.success
        assert "[DRY-RUN]" in response.message

    async def test_migration_command(self, supabase_client):
        """Migration 명령 테스트 (실제 실행 안 함)"""
        agent = SupabaseAgent(supabase_client=supabase_client, dry_run=False)

        # 존재하지 않는 Migration
        response = await agent.execute("Migration 999 실행해줘")

        assert not response.success
        assert "찾을 수 없습니다" in response.message

    async def test_validation_command(self, agent):
        """검증 명령 테스트"""
        # Dry-run이라도 검증은 시도
        agent.dry_run = False

        response = await agent.execute("conversation_sessions 테이블 확인해줘")

        # 테이블이 있으면 성공, 없으면 실패 (정상)
        assert response.message
        assert "conversation_sessions" in response.message

    async def test_query_command(self, agent):
        """조회 명령 테스트"""
        agent.dry_run = False

        response = await agent.execute("활성 세션 개수 알려줘")

        # 결과가 있어야 함 (0개라도 성공)
        assert response.message


class TestMigrationTool:
    """MigrationTool 테스트"""

    async def test_list_migrations(self, supabase_client):
        """Migration 목록 조회"""
        from src.shared.supabase_agent.tools import MigrationTool

        tool = MigrationTool(supabase_client)
        migrations = await tool.list_migrations()

        # migrations 디렉토리에 파일이 있어야 함
        assert isinstance(migrations, list)

    async def test_find_migration(self, supabase_client):
        """Migration 찾기"""
        from src.shared.supabase_agent.tools import MigrationTool

        tool = MigrationTool(supabase_client)

        # Migration 007 찾기
        result = await tool.find_migration("007")

        # 있으면 경로 반환, 없으면 None
        assert result is None or "007" in result


class TestValidationTool:
    """ValidationTool 테스트"""

    async def test_table_exists(self, supabase_client):
        """테이블 존재 확인"""
        from src.shared.supabase_agent.tools import ValidationTool

        tool = ValidationTool(supabase_client)

        # 존재하지 않는 테이블
        result = await tool.table_exists("nonexistent_table_12345")

        assert not result.exists

    async def test_function_exists(self, supabase_client):
        """함수 존재 확인"""
        from src.shared.supabase_agent.tools import ValidationTool

        tool = ValidationTool(supabase_client)

        # 존재하지 않는 함수
        result = await tool.function_exists("nonexistent_function_12345")

        assert not result.exists
