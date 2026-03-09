'use client'

import React, { useState } from 'react'
import { MapPin, ChevronDown } from 'lucide-react'

interface RegionSelectorProps {
  value?: string
  onChange?: (region: string) => void
  className?: string
}

export function RegionSelector({
  value = '청량리동',
  onChange,
  className = '',
}: RegionSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)

  const regions = [
    '청량리동',
    '회기동',
    '휘경동',
    '이문동',
    '장안동',
    '답십리동',
    '전농동',
    '용두동',
  ]

  const handleSelect = (region: string) => {
    if (onChange) {
      onChange(region)
    }
    setIsOpen(false)
  }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-background-main border border-background-border rounded-lg text-gray-200 hover:bg-background-hover transition-colors text-sm"
      >
        <MapPin className="w-4 h-4 text-primary" />
        <span className="font-medium">{value}</span>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full mt-2 left-0 w-48 bg-background-surface border border-background-border rounded-lg shadow-xl z-20 overflow-hidden">
            {regions.map((region) => (
              <button
                key={region}
                onClick={() => handleSelect(region)}
                className={`w-full text-left px-4 py-3 text-sm hover:bg-background-hover transition-colors ${
                  value === region
                    ? 'bg-primary/10 text-primary font-semibold'
                    : 'text-gray-300'
                }`}
              >
                {region}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
