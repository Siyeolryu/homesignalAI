import logging

import anthropic
import httpx
import openai

from src.config import settings

from .exceptions import AIAPIError

logger = logging.getLogger(__name__)


class AIClient:
    """OpenAI/Anthropic AI API 통합 클라이언트"""

    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.ai_provider
        self._openai: openai.AsyncOpenAI | None = None
        self._anthropic: anthropic.AsyncAnthropic | None = None

    def _get_openai_client(self) -> openai.AsyncOpenAI:
        if self._openai is None:
            self._openai = openai.AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=httpx.Timeout(settings.ai_api_timeout),
            )
        return self._openai

    def _get_anthropic_client(self) -> anthropic.AsyncAnthropic:
        if self._anthropic is None:
            self._anthropic = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key,
                timeout=httpx.Timeout(settings.ai_api_timeout),
            )
        return self._anthropic

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """AI 응답 생성"""
        try:
            if self.provider == "openai":
                return await self._generate_openai(
                    system_prompt,
                    user_message,
                    model or "gpt-4o",
                    temperature,
                    max_tokens,
                )
            else:
                return await self._generate_anthropic(
                    system_prompt,
                    user_message,
                    model or "claude-3-5-sonnet-20241022",
                    temperature,
                    max_tokens,
                )
        except Exception as e:
            logger.error(f"AI API 호출 실패 ({self.provider}): {e}")
            raise AIAPIError(
                message="AI 응답 생성에 실패했습니다.",
                details={"provider": self.provider, "error": str(e)},
            )

    async def generate_with_history(
        self,
        system_prompt: str,
        conversation_history: list[dict[str, str]],
        user_message: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        대화 히스토리를 포함한 AI 응답 생성

        Args:
            system_prompt: 시스템 프롬프트
            conversation_history: 이전 대화 메시지 리스트
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            user_message: 현재 사용자 메시지
            model: 사용할 모델 (선택사항)
            temperature: 온도 (기본값: 0.7)
            max_tokens: 최대 토큰 수 (기본값: 2048)

        Returns:
            str: AI 생성 응답
        """
        try:
            if self.provider == "openai":
                return await self._generate_openai_with_history(
                    system_prompt,
                    conversation_history,
                    user_message,
                    model or "gpt-4o",
                    temperature,
                    max_tokens,
                )
            else:
                return await self._generate_anthropic_with_history(
                    system_prompt,
                    conversation_history,
                    user_message,
                    model or "claude-3-5-sonnet-20241022",
                    temperature,
                    max_tokens,
                )
        except Exception as e:
            logger.error(f"AI API 호출 실패 (대화형, {self.provider}): {e}")
            raise AIAPIError(
                message="AI 응답 생성에 실패했습니다.",
                details={"provider": self.provider, "error": str(e)},
            )

    async def _generate_openai(
        self,
        system_prompt: str,
        user_message: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        client = self._get_openai_client()
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def _generate_anthropic(
        self,
        system_prompt: str,
        user_message: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        client = self._get_anthropic_client()
        response = await client.messages.create(
            model=model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content[0].text

    async def _generate_openai_with_history(
        self,
        system_prompt: str,
        conversation_history: list[dict[str, str]],
        user_message: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """OpenAI 대화 히스토리 포함 응답 생성"""
        client = self._get_openai_client()

        # 메시지 구성: system + 이전 대화 + 현재 메시지
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        logger.info(f"OpenAI API 호출: {len(messages)}개 메시지 (히스토리 포함)")

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def _generate_anthropic_with_history(
        self,
        system_prompt: str,
        conversation_history: list[dict[str, str]],
        user_message: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Anthropic 대화 히스토리 포함 응답 생성"""
        client = self._get_anthropic_client()

        # 메시지 구성: 이전 대화 + 현재 메시지
        messages = list(conversation_history)
        messages.append({"role": "user", "content": user_message})

        logger.info(f"Anthropic API 호출: {len(messages)}개 메시지 (히스토리 포함)")

        response = await client.messages.create(
            model=model,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content[0].text


_ai_client: AIClient | None = None


def get_ai_client() -> AIClient:
    """AI 클라이언트 싱글톤 반환"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
