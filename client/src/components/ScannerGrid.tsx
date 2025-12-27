import { useState, useEffect } from 'react'

const GRID_ROWS = 12
const GRID_COLS = 40

interface GridCell {
  scanned: boolean
  color: string
}

interface Issues {
  critical: number
  high: number
  medium: number
  low: number
}

interface ScannerGridProps {
  scanProgress: number
  issues: Issues
}

export function ScannerGrid({ scanProgress, issues }: ScannerGridProps) {
  const [grid, setGrid] = useState<GridCell[][]>([])

  useEffect(() => {
    const initialGrid: GridCell[][] = []
    for (let row = 0; row < GRID_ROWS; row++) {
      const rowData: GridCell[] = []
      for (let col = 0; col < GRID_COLS; col++) {
        rowData.push({
          scanned: false,
          color: 'gray'
        })
      }
      initialGrid.push(rowData)
    }
    setGrid(initialGrid)
  }, [])

  useEffect(() => {
    const totalCells = GRID_ROWS * GRID_COLS
    const scannedCells = Math.floor((scanProgress / 100) * totalCells)

    const getRandomColor = (): string => {
      const random = Math.random()
      const issueRatio = (issues.critical + issues.high + issues.medium + issues.low) / 50

      if (random > 0.97 && issues.critical > 0) return 'red'
      if (random > 0.94 && issues.high > 0) return 'orange'
      if (random > 0.91 && issues.medium > 0) return 'yellow'
      if (random > 0.88 && issues.low > 0) return 'lime'
      return 'green'
    }

    setGrid(prevGrid => {
      if (prevGrid.length === 0) return prevGrid
      
      const newGrid = prevGrid.map(row => row.map(cell => ({ ...cell })))

      let cellCount = 0
      for (let row = 0; row < GRID_ROWS; row++) {
        for (let col = 0; col < GRID_COLS; col++) {
          if (cellCount < scannedCells) {
            if (!newGrid[row][col].scanned) {
              newGrid[row][col].scanned = true
              newGrid[row][col].color = getRandomColor()
            }
          }
          cellCount++
        }
      }

      return newGrid
    })
  }, [scanProgress, issues])

  const getCellColorClass = (cell: GridCell): string => {
    if (!cell.scanned) return 'bg-gray-700'

    switch (cell.color) {
      case 'red': return 'bg-red-500'
      case 'orange': return 'bg-orange-500'
      case 'yellow': return 'bg-yellow-400'
      case 'lime': return 'bg-lime-400'
      case 'green': return 'bg-green-500'
      default: return 'bg-gray-700'
    }
  }

  return (
    <div className="bg-gray-900 p-4 rounded-lg">
      <div 
        className="grid gap-[2px]" 
        style={{ gridTemplateColumns: `repeat(${GRID_COLS}, 1fr)` }}
      >
        {grid.flat().map((cell, index) => (
          <div
            key={index}
            className={`h-3 rounded-sm transition-colors duration-150 ${getCellColorClass(cell)}`}
          />
        ))}
      </div>

      <div
        className="h-1 bg-blue-400 rounded mt-3 transition-all duration-300"
        style={{
          width: `${scanProgress}%`,
          boxShadow: '0 0 10px #60a5fa, 0 0 20px #60a5fa'
        }}
      />
    </div>
  )
}
