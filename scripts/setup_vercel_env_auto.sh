#!/bin/bash

# Vercel 환경변수 자동 설정 스크립트
# 사용법: ./scripts/setup_vercel_env_auto.sh

set -e

echo "=========================================="
echo "Vercel 환경변수 자동 설정"
echo "=========================================="
echo ""

# Supabase 환경변수 (VERCEL_DEPLOYMENT_GUIDE.md에서 가져옴)
SUPABASE_URL="https://yietqoikdaqpwmmvamtv.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlpZXRxb2lrZGFxcHdtbXZhbXR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMjMyNjksImV4cCI6MjA4NzU5OTI2OX0.cnGFGUsn05TpVIvZyk6Sn6jEUdkTPzqc9YHOLnPr6NY"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlpZXRxb2lrZGFxcHdtbXZhbXR2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAyMzI2OSwiZXhwIjoyMDg3NTk5MjY5fQ.F4HvWwUiFMysGP06DW45v5RbxG7UoW38q8JI2z1MIDM"

echo "1. Supabase 환경변수 설정 중..."
echo ""

# SUPABASE_URL
echo "Setting SUPABASE_URL..."
echo "$SUPABASE_URL" | vercel env add SUPABASE_URL production
echo "$SUPABASE_URL" | vercel env add SUPABASE_URL preview
echo "$SUPABASE_URL" | vercel env add SUPABASE_URL development
echo "✅ SUPABASE_URL 설정 완료"
echo ""

# SUPABASE_KEY
echo "Setting SUPABASE_KEY..."
echo "$SUPABASE_KEY" | vercel env add SUPABASE_KEY production
echo "$SUPABASE_KEY" | vercel env add SUPABASE_KEY preview
echo "$SUPABASE_KEY" | vercel env add SUPABASE_KEY development
echo "✅ SUPABASE_KEY 설정 완료"
echo ""

# SUPABASE_SERVICE_ROLE_KEY
echo "Setting SUPABASE_SERVICE_ROLE_KEY..."
echo "$SUPABASE_SERVICE_ROLE_KEY" | vercel env add SUPABASE_SERVICE_ROLE_KEY production
echo "$SUPABASE_SERVICE_ROLE_KEY" | vercel env add SUPABASE_SERVICE_ROLE_KEY preview
echo "$SUPABASE_SERVICE_ROLE_KEY" | vercel env add SUPABASE_SERVICE_ROLE_KEY development
echo "✅ SUPABASE_SERVICE_ROLE_KEY 설정 완료"
echo ""

echo "2. App 설정 환경변수 설정 중..."
echo ""

# APP_ENV
echo "Setting APP_ENV..."
echo "production" | vercel env add APP_ENV production
echo "preview" | vercel env add APP_ENV preview
echo "development" | vercel env add APP_ENV development
echo "✅ APP_ENV 설정 완료"
echo ""

# DEBUG
echo "Setting DEBUG..."
echo "false" | vercel env add DEBUG production
echo "false" | vercel env add DEBUG preview
echo "true" | vercel env add DEBUG development
echo "✅ DEBUG 설정 완료"
echo ""

# AI_PROVIDER
echo "Setting AI_PROVIDER..."
echo "openai" | vercel env add AI_PROVIDER production
echo "openai" | vercel env add AI_PROVIDER preview
echo "openai" | vercel env add AI_PROVIDER development
echo "✅ AI_PROVIDER 설정 완료"
echo ""

echo "3. OPENAI_API_KEY 설정 (수동 입력 필요)"
echo ""
echo "⚠️  OPENAI_API_KEY를 입력해주세요."
echo "    OpenAI API 키가 없다면 Enter를 눌러 건너뛰세요."
echo ""
read -p "OPENAI_API_KEY (선택사항): " OPENAI_KEY

if [ -n "$OPENAI_KEY" ]; then
    echo "Setting OPENAI_API_KEY..."
    echo "$OPENAI_KEY" | vercel env add OPENAI_API_KEY production
    echo "$OPENAI_KEY" | vercel env add OPENAI_API_KEY preview
    echo "$OPENAI_KEY" | vercel env add OPENAI_API_KEY development
    echo "✅ OPENAI_API_KEY 설정 완료"
else
    echo "⏭️  OPENAI_API_KEY 건너뛰기 (나중에 설정 가능)"
fi
echo ""

echo "=========================================="
echo "✅ 환경변수 설정 완료!"
echo "=========================================="
echo ""

echo "📋 설정된 환경변수 목록:"
vercel env ls

echo ""
echo "🚀 다음 단계:"
echo "   1. vercel --prod (프로덕션 배포)"
echo "   2. curl https://your-backend.vercel.app/health (검증)"
echo ""
echo "💡 OPENAI_API_KEY를 나중에 설정하려면:"
echo "   vercel env add OPENAI_API_KEY production"
echo ""
