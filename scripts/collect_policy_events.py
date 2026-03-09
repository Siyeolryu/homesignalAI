"""
정책 이벤트 수집 스크립트

config/policy_events.yaml의 이벤트를 policy_events 테이블에 적재합니다.

Usage:
    uv run python scripts/collect_policy_events.py
    uv run python scripts/collect_policy_events.py --dry-run
"""

import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path

import yaml

from src.shared.database import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_and_insert_events(dry_run: bool = False):
    """policy_events.yaml 로드 및 Supabase INSERT"""

    # YAML 파일 로드
    config_path = Path("config/policy_events.yaml")
    if not config_path.exists():
        logger.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    events = config.get("events", [])
    if not events:
        logger.warning("정책 이벤트가 없습니다.")
        return

    logger.info(f"로드된 이벤트 수: {len(events)}")

    # Supabase 클라이언트
    supabase = get_supabase_client()

    # 이벤트 INSERT
    inserted_count = 0
    skipped_count = 0

    for event in events:
        event_date = event["date"]
        event_type = event["type"]
        event_name = event["name"]
        description = event.get("description")
        impact_level = event.get("impact_level", "medium")
        region = event.get("region")

        if dry_run:
            logger.info(
                f"[DRY-RUN] {event_date} | {event_type} | {event_name} | {region or '전체'}"
            )
            continue

        try:
            # 중복 확인
            existing = (
                supabase.table("policy_events")
                .select("id")
                .eq("event_date", event_date)
                .eq("event_name", event_name)
                .execute()
            )

            if existing.data:
                logger.info(f"  ⊘ 이미 존재: {event_name}")
                skipped_count += 1
                continue

            # INSERT
            supabase.table("policy_events").insert(
                {
                    "event_date": event_date,
                    "event_type": event_type,
                    "event_name": event_name,
                    "description": description,
                    "impact_level": impact_level,
                    "region": region,
                }
            ).execute()

            logger.info(f"  ✓ 삽입 완료: {event_name}")
            inserted_count += 1

        except Exception as e:
            logger.error(f"  ✗ 삽입 실패: {event_name} - {e}")

    if not dry_run:
        logger.info(f"\n완료: {inserted_count}개 삽입, {skipped_count}개 스킵")
    else:
        logger.info(f"\n[DRY-RUN] 총 {len(events)}개 이벤트 확인됨")


async def main():
    parser = argparse.ArgumentParser(description="정책 이벤트 수집")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 INSERT 없이 미리보기만",
    )

    args = parser.parse_args()

    await load_and_insert_events(dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
