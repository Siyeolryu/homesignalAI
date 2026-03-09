'use client'

import React, { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface AccordionProps {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
  className?: string
}

export function Accordion({
  title,
  children,
  defaultOpen = false,
  className = '',
}: AccordionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className={`card-surface overflow-hidden ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-background-hover transition-colors"
      >
        <span className="text-lg font-semibold">{title}</span>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>
      
      {isOpen && (
        <div className="px-6 pb-6 pt-2 animate-slide-up">
          {children}
        </div>
      )}
    </div>
  )
}
