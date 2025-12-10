import { describe, it, expect } from 'vitest'

describe('Utility Functions', () => {
  describe('formatMachineName', () => {
    function formatMachineName(id: string): string {
      return id
        .replace(/[-_]/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    }

    it('formats hyphenated names', () => {
      expect(formatMachineName('molding-machine-1')).toBe('Molding Machine 1')
    })

    it('formats underscored names', () => {
      expect(formatMachineName('test_machine_name')).toBe('Test Machine Name')
    })

    it('handles mixed separators', () => {
      expect(formatMachineName('test-machine_name')).toBe('Test Machine Name')
    })
  })

  describe('formatDefectName', () => {
    function formatDefectName(name: string): string {
      if (!name) return ''
      return name
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ')
    }

    it('formats snake_case defect names', () => {
      expect(formatDefectName('knit_line_defect')).toBe('Knit Line Defect')
    })

    it('handles empty string', () => {
      expect(formatDefectName('')).toBe('')
    })

    it('handles single word', () => {
      expect(formatDefectName('void')).toBe('Void')
    })
  })
})