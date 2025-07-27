import React, { useState } from 'react';
import './App.css';

const API_URL = 'http://127.0.0.1:5001';

function shuffleArray<T>(array: T[]): T[] {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

const App: React.FC = () => {
  const [pieces, setPieces] = useState<string[]>([]);
  const [shuffledPieces, setShuffledPieces] = useState<string[]>([]);
  const [rebuiltUrl, setRebuiltUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shatterRuntime, setShatterRuntime] = useState<number | null>(null);
  const [rebuildRuntime, setRebuildRuntime] = useState<number | null>(null);
  const [modalPiece, setModalPiece] = useState<string | null>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    setLoading(true);
    setError(null);
    setRebuiltUrl(null);
    setPieces([]);
    setShuffledPieces([]);
    setShatterRuntime(null);
    setRebuildRuntime(null);
    const formData = new FormData();
    formData.append('image', e.target.files[0]);
    try {
      const res = await fetch(`${API_URL}/shatter`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.pieces && data.pieces.length === 50) {
        setPieces(data.pieces);
        setShuffledPieces(data.pieces);
        setShatterRuntime(data.runtime ?? null);
      } else if (data.pieces) {
        setError(`Expected 50 pieces, got ${data.pieces.length}. Try again.`);
      } else {
        setError(data.error || 'Failed to shatter image');
      }
    } catch (err) {
      setError('Failed to connect to backend');
    }
    setLoading(false);
  };

  const handleShuffle = () => {
    setShuffledPieces(shuffleArray(shuffledPieces));
    setRebuiltUrl(null);
  };

  const handleRebuild = async () => {
    setLoading(true);
    setError(null);
    setRebuiltUrl(null);
    setRebuildRuntime(null);
    try {
      const res = await fetch(`${API_URL}/rebuild`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order: shuffledPieces.map(url => url.split('/').pop() || '') }),
      });
      const data = await res.json();
      if (data.rebuilt) {
        setRebuiltUrl(`${API_URL}${data.rebuilt}`);
        setRebuildRuntime(data.runtime ?? null);
      } else {
        setError(data.error || 'Failed to rebuild image');
      }
    } catch (err) {
      setError('Failed to connect to backend');
    }
    setLoading(false);
  };

  const handleDownloadPieces = async () => {
    try {
      const res = await fetch(`${API_URL}/download_pieces_zip`);
      if (!res.ok) throw new Error('Failed to download zip');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pieces.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download pieces zip');
    }
  };

  // Add a cache-busting query param to each image to force reload
  const getPieceSrc = (piece: string) => `${API_URL}${piece}?t=${Date.now()}`;

  return (
    <div className="App">
      <div className="header-box">Image Shatter & Rebuild</div>
      <input type="file" accept="image/png" onChange={handleUpload} />
      {loading && (
        <div className="loader-puzzle">
          <div className="loader-piece" />
          <div className="loader-piece" />
          <div className="loader-piece" />
        </div>
      )}
      {error && <p style={{ color: 'red', margin: '16px 0' }}>{error}</p>}
      {pieces.length === 50 && (
        <>
          <div className="functions-row">
            <button className="shatter-btn" onClick={handleShuffle}>Shuffle Pieces</button>
            <div className="pieces-grid">
              {shuffledPieces.map((piece, idx) => (
                <div className="piece-card" key={piece + '-' + idx} onClick={() => setModalPiece(`${API_URL}${piece}`)} tabIndex={0} role="button" aria-label={`Zoom piece ${idx + 1}`}>
                  <img
                    src={getPieceSrc(piece)}
                    alt={`piece-${idx}`}
                  />
                </div>
              ))}
            </div>
            <button className="rebuild-btn" onClick={handleRebuild}>Rebuild Image</button>
          </div>
          {shatterRuntime !== null && (
            <div className="runtime-box">Shatter runtime: <span>{shatterRuntime.toFixed(2)}</span> seconds</div>
          )}
          {/* Modal for zoomed-in piece */}
          {modalPiece && (
            <div className="modal-bg" onClick={() => setModalPiece(null)}>
              <img
                src={modalPiece}
                alt="Zoomed piece"
                className="modal-img"
                onClick={e => e.stopPropagation()}
              />
            </div>
          )}
        </>
      )}
      {rebuiltUrl && (
        <div>
          <h2>Rebuilt Image</h2>
          <img
            src={rebuiltUrl ? rebuiltUrl + '?t=' + Date.now() : ''}
            alt="rebuilt"
            style={{ maxWidth: 400, border: '2px solid #185adb', borderRadius: 0, boxShadow: '0 4px 24px rgba(24,90,219,0.12)' }}
          />
          {rebuildRuntime !== null && (
            <p>Rebuild runtime: {rebuildRuntime.toFixed(2)} seconds</p>
          )}
        </div>
      )}
    </div>
  );
};

export default App;
