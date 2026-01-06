import React from 'react';
import { X } from 'lucide-react';
import { SECTION_COLORS, SECTION_OPTIONS } from './structureTypes';
import type { SectionType } from './structureTypes';

interface AddSectionModalProps {
  lineNumber: number;
  onAdd: (sectionType: SectionType) => void;
  onClose: () => void;
}

export const AddSectionModal: React.FC<AddSectionModalProps> = ({
  lineNumber,
  onAdd,
  onClose
}) => {
  return (
    <>
      <div 
        className="fixed inset-0 bg-black/30 z-50"
        onClick={onClose}
      />
      
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                      bg-white rounded-xl shadow-2xl z-50 w-80 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 
                        bg-gray-50 border-b">
          <div>
            <h3 className="font-semibold text-gray-800">Add Section Divider</h3>
            <p className="text-xs text-gray-500">At line {lineNumber}</p>
          </div>
          <button 
            onClick={onClose}
            className="p-1 hover:bg-gray-200 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        
        <div className="p-2 max-h-80 overflow-y-auto">
          <p className="px-2 py-1 text-xs text-gray-500 mb-1">
            Select section type:
          </p>
          
          {SECTION_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => onAdd(option.value)}
              className="w-full px-3 py-3 text-left hover:bg-gray-100 
                         rounded-lg flex items-center gap-3 transition-colors"
            >
              <div 
                className="w-4 h-4 rounded-full flex-shrink-0"
                style={{ backgroundColor: SECTION_COLORS[option.value]?.tab || '#6B7280' }}
              />
              
              <div>
                <div className="font-medium text-gray-800">{option.label}</div>
                <div className="text-xs text-gray-500">{option.description}</div>
              </div>
            </button>
          ))}
        </div>
        
        <div className="px-4 py-3 bg-gray-50 border-t">
          <button
            onClick={onClose}
            className="w-full py-2 text-sm text-gray-600 hover:bg-gray-200 
                       rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </>
  );
};

export default AddSectionModal;
