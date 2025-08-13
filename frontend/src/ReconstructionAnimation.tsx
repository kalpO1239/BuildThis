import React, { useState, useEffect } from 'react';

interface Position {
  top: number;
  left: number;
}

interface PieceCoordinate {
  piece_index: number;
  top: number;
  left: number;
}

interface Props {
  pieces: string[];
  pieceCoordinates: PieceCoordinate[];
  pieceDimensions: { height: number; width: number };
  gridSize: number;
  onAnimationComplete?: () => void;
}

const containerWidth = 800;
const containerHeight = 600;

const ReconstructionAnimation: React.FC<Props> = ({
  pieces,
  pieceCoordinates,
  pieceDimensions,
  gridSize,
  onAnimationComplete
}) => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);
  const [animationProgress, setAnimationProgress] = useState(0);

  // Scattered piece size (fixed for display)
  const pieceSizeScattered = 150;
  const padding = 5;

  useEffect(() => {
    if (!isAnimating) {
      // Initial scattered positions
      const scatteredPositions: Position[] = [];
      const maxAttempts = 1000;

      for (let i = 0; i < pieces.length; i++) {
        let attempts = 0;
        let position: Position;
        let overlaps: boolean;

        do {
          position = {
            top: Math.random() * (containerHeight - pieceSizeScattered),
            left: Math.random() * (containerWidth - pieceSizeScattered),
          };

          overlaps = scatteredPositions.some((pos) => {
            const dx = Math.abs(pos.left - position.left);
            const dy = Math.abs(pos.top - position.top);
            return (
              dx < pieceSizeScattered + padding &&
              dy < pieceSizeScattered + padding
            );
          });

          attempts++;
        } while (overlaps && attempts < maxAttempts);

        scatteredPositions.push(position);
      }

      setPositions(scatteredPositions);
    }
  }, [isAnimating, pieces]);

  const startAnimation = () => {
    if (pieceCoordinates.length === 0) return;
    
    setIsAnimating(true);
    setAnimationProgress(0);
    
    // Calculate final positions in the container
    const finalPositions: Position[] = [];
    const scaleX = containerWidth / (gridSize * pieceDimensions.width);
    const scaleY = containerHeight / (gridSize * pieceDimensions.height);
    const scale = Math.min(scaleX, scaleY, 1); // Don't scale up, only down
    
    for (const coord of pieceCoordinates) {
      finalPositions.push({
        top: (coord.top * scale) + (containerHeight - gridSize * pieceDimensions.height * scale) / 2,
        left: (coord.left * scale) + (containerWidth - gridSize * pieceDimensions.width * scale) / 2,
      });
    }
    
    // Animate from scattered to final positions
    const duration = 2000; // 2 seconds
    const startTime = Date.now();
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      
      const newPositions = positions.map((startPos, i) => {
        if (i < finalPositions.length) {
          const endPos = finalPositions[i];
          return {
            top: startPos.top + (endPos.top - startPos.top) * easeProgress,
            left: startPos.left + (endPos.left - startPos.left) * easeProgress,
          };
        }
        return startPos;
      });
      
      setPositions(newPositions);
      setAnimationProgress(easeProgress);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
        onAnimationComplete?.();
      }
    };
    
    requestAnimationFrame(animate);
  };

  const resetAnimation = () => {
    setIsAnimating(false);
    setAnimationProgress(0);
    // Reset to scattered positions
    setPositions([]);
    setTimeout(() => {
      setPositions(positions.map(() => ({
        top: Math.random() * (containerHeight - pieceSizeScattered),
        left: Math.random() * (containerWidth - pieceSizeScattered),
      })));
    }, 100);
  };

  return (
    <div>
      <div
        style={{
          position: 'relative',
          width: containerWidth,
          height: containerHeight,
          border: '1px solid #ccc',
          margin: '20px auto',
          background: '#f8f9fa',
          borderRadius: 12,
          overflow: 'hidden',
        }}
      >
        {pieces.map((src, i) => (
          <img
            key={i}
            src={src}
            alt={`piece-${i}`}
            style={{
              position: 'absolute',
              width: pieceSizeScattered,
              height: pieceSizeScattered,
              top: positions[i]?.top ?? 0,
              left: positions[i]?.left ?? 0,
              borderRadius: 8,
              cursor: 'pointer',
              transition: isAnimating ? 'none' : 'top 0.7s ease, left 0.7s ease',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
              objectFit: 'cover',
              opacity: isAnimating ? 0.8 : 1,
            }}
          />
        ))}
        
        {/* Grid overlay for reference */}
        {isAnimating && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              pointerEvents: 'none',
              opacity: 0.3,
            }}
          >
            {Array.from({ length: gridSize + 1 }).map((_, i) => (
              <React.Fragment key={i}>
                <div
                  style={{
                    position: 'absolute',
                    top: (i * containerHeight) / gridSize,
                    left: 0,
                    width: '100%',
                    height: '1px',
                    backgroundColor: '#007bff',
                  }}
                />
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: (i * containerWidth) / gridSize,
                    width: '1px',
                    height: '100%',
                    backgroundColor: '#007bff',
                  }}
                />
              </React.Fragment>
            ))}
          </div>
        )}
      </div>
      
      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        {!isAnimating ? (
          <button
            onClick={startAnimation}
            style={{
              padding: '12px 24px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: '#28a745',
              color: 'white',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '600',
              marginRight: '10px',
            }}
          >
            🎬 Start Reconstruction Animation
          </button>
        ) : (
          <div style={{ marginBottom: '10px' }}>
            <div style={{ 
              width: '200px', 
              height: '8px', 
              backgroundColor: '#e9ecef', 
              borderRadius: '4px', 
              margin: '0 auto 10px auto',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${animationProgress * 100}%`,
                height: '100%',
                backgroundColor: '#28a745',
                transition: 'width 0.1s ease',
              }} />
            </div>
            <span style={{ fontSize: '14px', color: '#6c757d' }}>
              Reconstructing... {Math.round(animationProgress * 100)}%
            </span>
          </div>
        )}
        
        <button
          onClick={resetAnimation}
          style={{
            padding: '10px 20px',
            borderRadius: '8px',
            border: '1px solid #6c757d',
            backgroundColor: 'transparent',
            color: '#6c757d',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
          }}
        >
          🔄 Reset
        </button>
      </div>
    </div>
  );
};

export default ReconstructionAnimation;
