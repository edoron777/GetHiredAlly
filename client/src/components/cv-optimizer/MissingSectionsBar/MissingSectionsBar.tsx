import React from 'react'
import { Lightbulb, BookOpen } from 'lucide-react'

const ALL_SECTIONS = [
  'CONTACT',
  'HEADLINE', 
  'SUMMARY',
  'EXPERIENCE',
  'SKILLS',
  'EDUCATION',
  'CERTIFICATIONS',
  'PROJECTS',
  'LANGUAGES'
]

const SECTION_NAMES: Record<string, string> = {
  CONTACT: 'Contact Info',
  HEADLINE: 'Headline',
  SUMMARY: 'Summary',
  EXPERIENCE: 'Experience',
  SKILLS: 'Skills',
  EDUCATION: 'Education',
  CERTIFICATIONS: 'Certifications',
  PROJECTS: 'Projects',
  LANGUAGES: 'Languages'
}

interface MissingSectionsBarProps {
  detectedSections: string[]
  onSectionClick: (sectionKey: string) => void
  isVisible: boolean
}

export const MissingSectionsBar: React.FC<MissingSectionsBarProps> = ({
  detectedSections,
  onSectionClick,
  isVisible
}) => {
  if (!isVisible) return null
  
  const missingSections = ALL_SECTIONS.filter(
    section => !detectedSections.includes(section)
  )
  
  if (missingSections.length === 0) return null
  
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mt-4">
      <div className="flex items-center gap-2 mb-3">
        <BookOpen size={16} className="text-amber-700" />
        <span className="text-sm font-medium text-amber-800">
          Sections Not Found in Your CV
        </span>
        <span className="text-xs text-amber-600 ml-2">
          (Click to learn more)
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {missingSections.map(section => (
          <button
            key={section}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-sm text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors"
            onClick={() => onSectionClick(section)}
            title={`Learn about ${SECTION_NAMES[section]} section`}
          >
            <Lightbulb size={14} className="text-amber-500" />
            <span>{SECTION_NAMES[section]}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default MissingSectionsBar
