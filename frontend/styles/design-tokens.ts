/**
 * HomeSignal AI Design Tokens
 * 
 * 디자인 시스템 가이드 기반 컬러, 타이포그래피, 스페이싱 정의
 */

export const colors = {
  background: {
    main: '#0B1220',      // Deep Navy - 전체 배경
    surface: '#111827',   // Card background
    hover: '#1F2937',     // Hover state
    border: '#374151',    // Border color
  },
  primary: {
    main: '#4ADE80',      // Mint - 브랜드 컬러, 긍정/상승
    light: '#86EFAC',
    dark: '#22C55E',
    bg: 'rgba(74, 222, 128, 0.1)',  // 배경용
  },
  accent: {
    main: '#3B82F6',      // Electric Blue - AI 데이터, 예측선
    light: '#60A5FA',
    dark: '#2563EB',
    bg: 'rgba(59, 130, 246, 0.1)',
  },
  danger: {
    main: '#EF4444',      // Red - 경고
    light: '#F87171',
    dark: '#DC2626',
    bg: 'rgba(239, 68, 68, 0.1)',
  },
  warning: {
    main: '#F59E0B',      // Amber - 주의
    light: '#FCD34D',
    dark: '#D97706',
    bg: 'rgba(245, 158, 11, 0.1)',
  },
  negative: {
    main: '#FB7185',      // Soft Red - 부정 시그널
    light: '#FDA4AF',
    dark: '#F43F5E',
    bg: 'rgba(251, 113, 133, 0.1)',
  },
  teal: {
    main: '#14B8A6',      // Teal - 적정 공급
    light: '#2DD4BF',
    dark: '#0F766E',
  },
  orange: {
    main: '#EA580C',      // Orange - 과다 공급
    light: '#FB923C',
    dark: '#C2410C',
  },
  deepRed: {
    main: '#991B1B',      // Deep Red - 과잉 경고
    light: '#B91C1C',
    dark: '#7F1D1D',
  },
  text: {
    primary: '#F9FAFB',   // White
    secondary: '#D1D5DB', // Gray
    muted: '#9CA3AF',     // Muted gray
    disabled: '#6B7280',  // Disabled
  },
  gridDot: 'rgba(255, 255, 255, 0.05)',  // 배경 패턴
}

export const typography = {
  fontFamily: {
    sans: 'Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif',
    mono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
  },
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px
    '3xl': '1.875rem',  // 30px
    '4xl': '2.25rem',   // 36px
    '5xl': '3rem',      // 48px
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
}

export const spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
}

export const borderRadius = {
  sm: '0.25rem',   // 4px
  md: '0.5rem',    // 8px
  lg: '0.75rem',   // 12px
  xl: '1rem',      // 16px
  full: '9999px',  // Fully rounded
}

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
}

export const animation = {
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
  },
  easing: {
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
}

// Chart 테마
export const chartTheme = {
  actual: {
    stroke: '#FFFFFF',
    strokeWidth: 1.5,
    strokeDasharray: undefined,
  },
  predicted: {
    stroke: '#3B82F6',
    strokeWidth: 2,
    strokeDasharray: '5 5',
  },
  confidenceBand: {
    fill: '#3B82F6',
    fillOpacity: 0.15,
  },
  grid: {
    stroke: '#374151',
    strokeDasharray: '3 3',
  },
  axis: {
    stroke: '#6B7280',
  },
  tooltip: {
    background: '#1F2937',
    border: '#374151',
    text: '#F9FAFB',
  },
}

// 변동성 등급 컬러
export const volatilityGrades = {
  A: {
    color: '#4ADE80',  // 낮음 (안정)
    label: '낮음',
    bg: 'rgba(74, 222, 128, 0.1)',
  },
  B: {
    color: '#F59E0B',  // 보통
    label: '보통',
    bg: 'rgba(245, 158, 11, 0.1)',
  },
  C: {
    color: '#EF4444',  // 높음 (주의)
    label: '높음',
    bg: 'rgba(239, 68, 68, 0.1)',
  },
}

// 공급 히트맵 범례
export const supplyHeatmap = {
  stable: {
    color: '#14B8A6',  // Teal - 적정
    label: '적정',
  },
  moderate: {
    color: '#F59E0B',  // Amber - 보통
    label: '보통',
  },
  high: {
    color: '#EA580C',  // Orange - 과다
    label: '과다',
  },
  critical: {
    color: '#991B1B',  // Deep Red - 과잉 경고
    label: '과잉 경고',
  },
}
