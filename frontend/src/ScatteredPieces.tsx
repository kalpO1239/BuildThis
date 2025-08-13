import React, { useState, useEffect } from 'react';

interface Position {
  top: number;
  left: number;
}
interface Props {
  pieces: string[];
  originalPositions: Position[]; // Array of original positions in px relative to original image
  originalImageSize: { width: number; height: number }; // Original full image size in px
  pieceSize: number; // original piece width/height (assumed square)
}

const containerWidth = 800;
const containerHeight = 400;

const ScatteredPieces: React.FC<Props> = ({
  pieces,
  originalPositions,
  originalImageSize,
  pieceSize,
}) => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [rebuild, setRebuild] = useState(false);

  // Scattered piece size (fixed)
  const pieceSizeScattered = 300;
  const padding = 5; // small gap between pieces to avoid touching edges

  useEffect(() => {
    if (!rebuild) {
      // Scatter pieces randomly inside container **without overlapping**
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
    } else {
      // Rebuild: convert original positions (px) to container-relative positions
      // by treating original positions as fractions of original image size
      const rebuiltPositions = originalPositions.map((pos) => ({
        top: (pos.top / originalImageSize.height) * containerHeight,
        left: (pos.left / originalImageSize.width) * containerWidth,
      }));
      setPositions(rebuiltPositions);
    }
  }, [rebuild, pieces, originalPositions, originalImageSize]);

  return (
    <div>
      <div
        style={{
          position: 'relative',
          width: containerWidth,
          height: containerHeight,
          border: '1px solid #ccc',
          margin: '20px auto',
          background: '#eee',
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
              transition: 'top 0.7s ease, left 0.7s ease, width 0.7s ease, height 0.7s ease',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
              objectFit: 'cover',
            }}
          />
        ))}
      </div>
      <div style={{ textAlign: 'center' }}>
        <button
          onClick={() => setRebuild((prev) => !prev)}
          style={{
            padding: '10px 20px',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: '#007bff',
            color: 'white',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '600',
            marginTop: 10,
          }}
        >
          {rebuild ? 'Scatter Again' : 'Rebuild'}
        </button>
      </div>
    </div>
  );
};

export default ScatteredPieces;