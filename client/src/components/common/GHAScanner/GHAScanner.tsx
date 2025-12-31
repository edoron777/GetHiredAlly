import { useState, useEffect, useRef } from 'react';
import { SCANNER_STYLES } from './scannerStyles';

const { gridRows: GRID_ROWS, gridCols: GRID_COLS } = SCANNER_STYLES;

type CellStatus = 'waiting' | 'scanning' | 'green' | 'yellow' | 'orange' | 'red' | 'fixing' | 'fixed';

interface GridCell {
  status: CellStatus;
  originalIssue?: 'yellow' | 'orange' | 'red';
}

export interface GHAScannerProps {
  progress: number;
  showLegend?: boolean;
  showProgress?: boolean;
}

export function GHAScanner({ progress, showLegend = true, showProgress = true }: GHAScannerProps) {
  const [grid, setGrid] = useState<GridCell[][]>([]);
  const [scanLineRow, setScanLineRow] = useState(-1);
  const fixTimeouts = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  useEffect(() => {
    const initialGrid: GridCell[][] = [];
    for (let row = 0; row < GRID_ROWS; row++) {
      const rowData: GridCell[] = [];
      for (let col = 0; col < GRID_COLS; col++) {
        rowData.push({ status: 'waiting' });
      }
      initialGrid.push(rowData);
    }
    setGrid(initialGrid);

    return () => {
      fixTimeouts.current.forEach(timeout => clearTimeout(timeout));
    };
  }, []);

  useEffect(() => {
    const totalCells = GRID_ROWS * GRID_COLS;
    const scannedCells = Math.floor((progress / 100) * totalCells);
    const currentRow = Math.floor(scannedCells / GRID_COLS);
    setScanLineRow(currentRow);

    const getRandomStatus = (): CellStatus => {
      const random = Math.random();
      if (random < 0.02) return 'red';
      if (random < 0.07) return 'orange';
      if (random < 0.15) return 'yellow';
      return 'green';
    };

    setGrid(prevGrid => {
      if (prevGrid.length === 0) return prevGrid;
      
      const newGrid = prevGrid.map(row => row.map(cell => ({ ...cell })));

      let cellCount = 0;
      for (let row = 0; row < GRID_ROWS; row++) {
        for (let col = 0; col < GRID_COLS; col++) {
          const cellKey = `${row}-${col}`;
          
          if (cellCount < scannedCells) {
            if (newGrid[row][col].status === 'waiting') {
              const isCurrentlyScanning = cellCount >= scannedCells - GRID_COLS;
              
              if (isCurrentlyScanning && Math.random() > 0.7) {
                newGrid[row][col].status = 'scanning';
              } else {
                const newStatus = getRandomStatus();
                newGrid[row][col].status = newStatus;
                
                if (newStatus === 'red' || newStatus === 'orange' || newStatus === 'yellow') {
                  newGrid[row][col].originalIssue = newStatus;
                  
                  if (!fixTimeouts.current.has(cellKey)) {
                    const delay = 500 + Math.random() * 1000;
                    const timeout = setTimeout(() => {
                      setGrid(g => {
                        const updated = g.map(r => r.map(c => ({ ...c })));
                        if (updated[row] && updated[row][col]) {
                          updated[row][col].status = 'fixing';
                          
                          setTimeout(() => {
                            setGrid(g2 => {
                              const fixed = g2.map(r => r.map(c => ({ ...c })));
                              if (fixed[row] && fixed[row][col]) {
                                fixed[row][col].status = 'fixed';
                              }
                              return fixed;
                            });
                          }, 200);
                        }
                        return updated;
                      });
                      fixTimeouts.current.delete(cellKey);
                    }, delay);
                    fixTimeouts.current.set(cellKey, timeout);
                  }
                }
              }
            } else if (newGrid[row][col].status === 'scanning') {
              const newStatus = getRandomStatus();
              newGrid[row][col].status = newStatus;
            }
          }
          cellCount++;
        }
      }

      return newGrid;
    });
  }, [progress]);

  const getCellStyle = (_cell: GridCell, rowIndex: number): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      transition: 'all 0.15s ease-out'
    };

    if (rowIndex === scanLineRow) {
      baseStyle.boxShadow = '0 0 4px rgba(59, 130, 246, 0.8)';
    }

    return baseStyle;
  };

  const getCellColorClass = (cell: GridCell): string => {
    switch (cell.status) {
      case 'waiting':
        return 'bg-gray-700';
      case 'scanning':
        return 'bg-blue-400 animate-pulse';
      case 'green':
        return 'bg-green-500';
      case 'yellow':
        return 'bg-yellow-400';
      case 'orange':
        return 'bg-orange-500';
      case 'red':
        return 'bg-red-500';
      case 'fixing':
        return 'bg-white animate-pulse';
      case 'fixed':
        return 'bg-green-400';
      default:
        return 'bg-gray-700';
    }
  };

  return (
    <div className="bg-gray-900 p-4 rounded-lg relative overflow-hidden">
      <div 
        className="grid gap-[2px]" 
        style={{ gridTemplateColumns: `repeat(${GRID_COLS}, 1fr)` }}
      >
        {grid.flat().map((cell, index) => {
          const rowIndex = Math.floor(index / GRID_COLS);
          return (
            <div
              key={index}
              className={`h-3 rounded-sm ${getCellColorClass(cell)}`}
              style={getCellStyle(cell, rowIndex)}
            />
          );
        })}
      </div>

      {scanLineRow >= 0 && scanLineRow < GRID_ROWS && (
        <div
          className="absolute left-4 right-4 h-[2px] pointer-events-none"
          style={{
            top: `${16 + (scanLineRow * (12 + 2)) + 6}px`,
            background: 'linear-gradient(90deg, transparent, #60a5fa, #3b82f6, #60a5fa, transparent)',
            boxShadow: '0 0 8px #60a5fa, 0 0 16px #3b82f6',
            animation: 'pulse 1s ease-in-out infinite'
          }}
        />
      )}

      {showProgress && (
        <div
          className="h-1 bg-blue-400 rounded mt-3 transition-all duration-300"
          style={{
            width: `${progress}%`,
            boxShadow: '0 0 10px #60a5fa, 0 0 20px #60a5fa'
          }}
        />
      )}

      {showLegend && (
        <div className="flex justify-between mt-3 text-xs">
          <div className="flex gap-3">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-green-500"></span>
              <span className="text-gray-400">Polish</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-yellow-400"></span>
              <span className="text-gray-400">Consider</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-orange-500"></span>
              <span className="text-gray-400">Important</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-red-500"></span>
              <span className="text-gray-400">Critical</span>
            </span>
          </div>
          <div className="flex gap-3">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-blue-400 animate-pulse"></span>
              <span className="text-gray-400">Scanning</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-gray-700"></span>
              <span className="text-gray-400">Pending</span>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
