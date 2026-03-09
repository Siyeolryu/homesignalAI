'use client'

import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { MessageSquare, Send, Bot, User, ExternalLink } from 'lucide-react'
import { sendChatMessage } from '@/lib/api-client'
import { Badge } from '@/components'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{ title: string; url: string }>
  sentiment?: 'positive' | 'negative' | 'neutral'
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        '안녕하세요! 동대문구 부동산에 대해 궁금한 점을 물어보세요. 뉴스 데이터와 예측 정보를 바탕으로 답변해드립니다.',
      sentiment: 'neutral',
    },
  ])
  const [input, setInput] = useState('')
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const mutation = useMutation({
    mutationFn: (message: string) => sendChatMessage(message, sessionId),
    onSuccess: (data) => {
      const sentiment = detectSentiment(data.response)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          sources: data.sources,
          sentiment,
        },
      ])
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
          sentiment: 'neutral',
        },
      ])
    },
  })

  const detectSentiment = (text: string): 'positive' | 'negative' | 'neutral' => {
    const positiveKeywords = ['상승', '증가', '개선', '호재', '긍정', '성장', '확대']
    const negativeKeywords = ['하락', '감소', '악화', '악재', '부정', '위축', '축소']
    
    const hasPositive = positiveKeywords.some(kw => text.includes(kw))
    const hasNegative = negativeKeywords.some(kw => text.includes(kw))
    
    if (hasPositive && !hasNegative) return 'positive'
    if (hasNegative && !hasPositive) return 'negative'
    return 'neutral'
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || mutation.isPending) return

    const userMessage = input.trim()
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setInput('')
    mutation.mutate(userMessage)
  }

  const suggestedQuestions = [
    '청량리 부동산 가격이 오를까요?',
    'GTX-C가 부동산 시장에 미치는 영향은?',
    '이문휘경뉴타운 재개발 현황은?',
    '동대문구에서 투자하기 좋은 지역은?',
  ]

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <MessageSquare className="w-8 h-8 mr-3 text-primary" />
          AI 챗봇
        </h1>
      </div>

      {/* Chat Container */}
      <div className="card-surface flex flex-col h-[calc(100%-4rem)]">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`flex items-start gap-3 max-w-[80%] ${
                  message.role === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <div
                  className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                    message.role === 'user'
                      ? 'bg-accent'
                      : 'bg-background-hover'
                  }`}
                >
                  {message.role === 'user' ? (
                    <User className="w-5 h-5 text-white" />
                  ) : (
                    <Bot className="w-5 h-5 text-primary" />
                  )}
                </div>
                
                <div className="flex-1">
                  <div
                    className={`rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-accent text-white'
                        : 'bg-background-main border border-background-border'
                    }`}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">
                      {message.content}
                    </p>
                  </div>
                  
                  {message.role === 'assistant' && message.sentiment && message.sentiment !== 'neutral' && (
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-xs text-gray-500">감성 시그널:</span>
                      <Badge variant={message.sentiment}>
                        {message.sentiment === 'positive' ? '긍정적' : '부정적'}
                      </Badge>
                    </div>
                  )}
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs text-gray-500 font-medium">출처:</p>
                      {message.sources.map((source, idx) => (
                        <a
                          key={idx}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 text-xs text-accent hover:text-accent-light transition-colors p-2 bg-background-hover rounded-md group"
                        >
                          <ExternalLink className="w-3 h-3 flex-shrink-0" />
                          <span className="flex-1 line-clamp-1">{source.title}</span>
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {mutation.isPending && (
            <div className="flex justify-start">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-background-hover flex items-center justify-center">
                  <Bot className="w-5 h-5 text-primary" />
                </div>
                <div className="bg-background-main border border-background-border rounded-lg p-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions */}
        {messages.length === 1 && (
          <div className="px-6 pb-4 border-t border-background-border pt-4">
            <p className="text-sm text-gray-500 mb-3">추천 질문:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {suggestedQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInput(question)}
                  className="text-left text-sm p-3 bg-background-hover rounded-lg hover:bg-background-border transition-colors text-gray-300"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Form */}
        <form
          onSubmit={handleSubmit}
          className="border-t border-background-border p-4"
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="메시지를 입력하세요..."
              className="flex-1 px-4 py-3 bg-background-main border border-background-border rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={mutation.isPending}
            />
            <button
              type="submit"
              disabled={!input.trim() || mutation.isPending}
              className="px-6 py-3 bg-primary text-background-main rounded-lg hover:bg-primary-light disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors flex items-center font-semibold"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
