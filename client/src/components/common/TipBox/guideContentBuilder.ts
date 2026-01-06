/**
 * Guide Content Builder
 * 
 * Fetches CV section guide content from backend API and formats
 * it for display in TipBox with mode="guide".
 * 
 * @module guideContentBuilder
 * @version 1.0
 */

import { getAuthToken } from '@/lib/auth'
import type { TipBoxSection, RequirementItem } from './types'

export interface SectionGuideData {
  section_key: string
  section_display_name: string
  section_icon: string
  about_section: string
  purpose_benefits: string
  best_practices: string[]
  requirements: RequirementItem[]
  example_good: string
  example_bad: string
  common_mistakes: string[]
  position_guidance: string | null
  ats_tips: string | null
  is_mandatory_section: boolean
}

export interface GuideContent {
  title: string
  sections: TipBoxSection[]
  isMandatory: boolean
}

const guideCache = new Map<string, SectionGuideData>()
let cacheLoaded = false

async function loadGuideCache(): Promise<void> {
  if (cacheLoaded) return
  
  try {
    const token = getAuthToken()
    const response = await fetch(`/api/cv/section-guides?token=${token}`)
    
    if (!response.ok) {
      console.error('Failed to load section guides:', response.status)
      return
    }
    
    const data = await response.json()
    
    data?.forEach((guide: SectionGuideData) => {
      guideCache.set(guide.section_key, guide)
    })
    
    cacheLoaded = true
  } catch (error) {
    console.error('Failed to load section guides:', error)
  }
}

export async function buildGuideContent(sectionKey: string): Promise<GuideContent | null> {
  await loadGuideCache()
  
  const guide = guideCache.get(sectionKey)
  if (!guide) {
    console.warn(`No guide found for section: ${sectionKey}`)
    return null
  }
  
  const sections: TipBoxSection[] = [
    {
      type: 'text',
      label: 'ABOUT THIS SECTION',
      content: guide.about_section
    },
    {
      type: 'text',
      label: 'PURPOSE & BENEFITS',
      content: guide.purpose_benefits
    },
    {
      type: 'instructions',
      label: 'BEST PRACTICES',
      content: guide.best_practices.join('\n• ')
    },
    {
      type: 'requirements',
      label: 'REQUIREMENTS',
      requirements: guide.requirements
    },
    {
      type: 'example-correct',
      label: 'GOOD EXAMPLE',
      content: guide.example_good
    },
    {
      type: 'warning',
      label: 'COMMON MISTAKES TO AVOID',
      content: guide.common_mistakes.join('\n')
    },
    {
      type: 'example-wrong',
      label: 'POOR EXAMPLE',
      content: guide.example_bad
    }
  ]
  
  if (guide.position_guidance) {
    sections.push({
      type: 'text',
      label: 'POSITION IN CV',
      content: guide.position_guidance
    })
  }
  
  if (guide.ats_tips) {
    sections.push({
      type: 'text',
      label: '🤖 ATS OPTIMIZATION TIPS',
      content: guide.ats_tips
    })
  }
  
  return {
    title: `${guide.section_icon} ${guide.section_display_name}`,
    sections,
    isMandatory: guide.is_mandatory_section
  }
}

export async function getAllSectionKeys(): Promise<string[]> {
  await loadGuideCache()
  return Array.from(guideCache.keys())
}

export async function isSectionMandatory(sectionKey: string): Promise<boolean> {
  await loadGuideCache()
  return guideCache.get(sectionKey)?.is_mandatory_section ?? false
}

export function clearGuideCache(): void {
  guideCache.clear()
  cacheLoaded = false
}
