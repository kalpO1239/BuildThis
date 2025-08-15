import React, { useState, useEffect, useRef } from 'react';
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

// Mini-game component - Dice Rolling Game
const LoadingGame: React.FC<{ theme: any }> = ({ theme }) => {
  const [dice1, setDice1] = useState(1);
  const [dice2, setDice2] = useState(1);
  const [isRolling, setIsRolling] = useState(false);
  const [rollCount, setRollCount] = useState(0);
  const [total, setTotal] = useState(2);

  const rollDice = () => {
    if (isRolling) return;
    
    setIsRolling(true);
    setRollCount(prev => prev + 1);
    
    // Animate dice rolling
    let rollDuration = 0;
    const rollInterval = setInterval(() => {
      setDice1(Math.floor(Math.random() * 6) + 1);
      setDice2(Math.floor(Math.random() * 6) + 1);
      rollDuration += 100;
      
      if (rollDuration >= 1000) {
        clearInterval(rollInterval);
        setIsRolling(false);
        const finalDice1 = Math.floor(Math.random() * 6) + 1;
        const finalDice2 = Math.floor(Math.random() * 6) + 1;
        setDice1(finalDice1);
        setDice2(finalDice2);
        setTotal(finalDice1 + finalDice2);
      }
    }, 100);
  };

  const getDiceFace = (number: number) => {
    const dots = [];
    const positions = {
      1: [[1, 1]],
      2: [[0, 0], [2, 2]],
      3: [[0, 0], [1, 1], [2, 2]],
      4: [[0, 0], [0, 2], [2, 0], [2, 2]],
      5: [[0, 0], [0, 2], [1, 1], [2, 0], [2, 2]],
      6: [[0, 0], [0, 1], [0, 2], [2, 0], [2, 1], [2, 2]]
    };
    
    positions[number as keyof typeof positions].forEach(([row, col]) => {
      dots.push(
        <div
          key={`${row}-${col}`}
          style={{
            position: 'absolute',
            top: `${(row + 0.5) * 33.33}%`,
            left: `${(col + 0.5) * 33.33}%`,
            width: '10px',
            height: '10px',
            backgroundColor: '#333',
            borderRadius: '50%',
            transform: 'translate(-50%, -50%)',
            boxShadow: 'inset 0 1px 2px rgba(255,255,255,0.3)'
          }}
        />
      );
    });
    
    return dots;
  };

  useEffect(() => {
    // Auto-roll every 3 seconds
    const autoRoll = setInterval(() => {
      rollDice();
    }, 3000);

    return () => clearInterval(autoRoll);
  }, [isRolling]);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: theme.surface,
        borderRadius: '20px',
        padding: '30px',
        maxWidth: '500px',
        width: '90%',
        textAlign: 'center',
        boxShadow: theme.shadowLarge,
        border: `1px solid ${theme.border}`
      }}>
        <h2 style={{ color: theme.text, margin: '0 0 20px 0' }}>
          🎲 Dice Rolling Game
        </h2>
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          marginBottom: '20px',
          fontSize: '16px',
          color: theme.textSecondary
        }}>
          <span>Rolls: {rollCount}</span>
          <span>Total: {total}</span>
        </div>

        {/* Dice Container */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '20px',
          marginBottom: '30px'
        }}>
          {/* Dice 1 */}
          <div style={{
            width: '80px',
            height: '80px',
            backgroundColor: 'white',
            border: `2px solid #ccc`,
            borderRadius: '8px',
            position: 'relative',
            transform: isRolling ? 'rotate(360deg)' : 'rotate(0deg)',
            transition: isRolling ? 'transform 0.1s linear' : 'transform 0.3s ease',
            boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
            background: 'linear-gradient(145deg, #ffffff 0%, #f0f0f0 100%)'
          }}>
            {getDiceFace(dice1)}
          </div>

          {/* Dice 2 */}
          <div style={{
            width: '80px',
            height: '80px',
            backgroundColor: 'white',
            border: `2px solid #ccc`,
            borderRadius: '8px',
            position: 'relative',
            transform: isRolling ? 'rotate(-360deg)' : 'rotate(0deg)',
            transition: isRolling ? 'transform 0.1s linear' : 'transform 0.3s ease',
            boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
            background: 'linear-gradient(145deg, #ffffff 0%, #f0f0f0 100%)'
          }}>
            {getDiceFace(dice2)}
          </div>
        </div>

        {/* Roll Button */}
        <button
          onClick={rollDice}
          disabled={isRolling}
          style={{
            backgroundColor: isRolling ? theme.textMuted : theme.primary,
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            cursor: isRolling ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: '500',
            marginBottom: '20px',
            transition: 'all 0.2s ease'
          }}
        >
          {isRolling ? '🎲 Rolling...' : '🎲 Roll Dice'}
        </button>

        {/* Stats */}
        <div style={{ marginBottom: '20px' }}>
          <p style={{ 
            color: theme.textSecondary, 
            fontSize: '14px',
            margin: '0 0 10px 0'
          }}>
            Dice 1: {dice1} | Dice 2: {dice2}
          </p>
          <p style={{ 
            color: theme.textSecondary, 
            fontSize: '14px',
            margin: '0'
          }}>
            Auto-rolls every 3 seconds, or click to roll manually!
          </p>
        </div>

        {/* Special Messages */}
        {total === 7 && (
          <div style={{
            backgroundColor: theme.accent,
            color: 'white',
            padding: '10px',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            🍀 Lucky 7!
          </div>
        )}
        {total === 12 && (
          <div style={{
            backgroundColor: theme.warning,
            color: 'white',
            padding: '10px',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            🎯 Boxcars!
          </div>
        )}
        {total === 2 && (
          <div style={{
            backgroundColor: theme.danger,
            color: 'white',
            padding: '10px',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            🐍 Snake Eyes!
          </div>
        )}

        <p style={{ 
          color: theme.textMuted, 
          fontSize: '12px', 
          margin: '20px 0 0 0',
          fontStyle: 'italic'
        }}>
          Processing your puzzle... This might take a while! 🧩
        </p>
      </div>
    </div>
  );
};

// Theme configuration
const themes = {
  light: {
    primary: '#3b82f6',
    primaryHover: '#2563eb',
    secondary: '#6b7280',
    accent: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    background: '#ffffff',
    surface: '#f9fafb',
    surfaceHover: '#f3f4f6',
    border: '#e5e7eb',
    text: '#111827',
    textSecondary: '#6b7280',
    textMuted: '#9ca3af',
    shadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    shadowLarge: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  },
  dark: {
    primary: '#3b82f6',
    primaryHover: '#2563eb',
    secondary: '#9ca3af',
    accent: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    background: '#111827',
    surface: '#1f2937',
    surfaceHover: '#374151',
    border: '#374151',
    text: '#f9fafb',
    textSecondary: '#d1d5db',
    textMuted: '#9ca3af',
    shadow: '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)',
    shadowLarge: '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
  }
};

const App: React.FC = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedZipFile, setUploadedZipFile] = useState<File | null>(null);
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [pieces, setPieces] = useState<string[]>([]);
  const [shuffledPieces, setShuffledPieces] = useState<string[]>([]);
  const [originalImageSize, setOriginalImageSize] = useState<any>(null);
  const [shattered, setShattered] = useState(false);
  const [rebuiltUrl, setRebuiltUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shatterRuntime, setShatterRuntime] = useState<number | null>(null);
  const [rebuildRuntime, setRebuildRuntime] = useState<number | null>(null);
  const [modalPiece, setModalPiece] = useState<string | null>(null);
  const [timingBreakdown, setTimingBreakdown] = useState<any>(null);
  const [rebuildTimingBreakdown, setRebuildTimingBreakdown] = useState<any>(null);
  const [placementData, setPlacementData] = useState<any>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [scatteredPieces, setScatteredPieces] = useState<any[]>([]);
  const [animationPhase, setAnimationPhase] = useState<'scattered' | 'moving' | 'complete'>('scattered');
  const animationRef = useRef<any[]>([]);
  const animationIdRef = useRef<number>(0);
  const currentPlacementDataRef = useRef<any>(null);
  const [currentPieceIndex, setCurrentPieceIndex] = useState<number>(0);
  const pieceCount = 50; // Fixed at 50 pieces
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showGame, setShowGame] = useState(false);

  const theme = isDarkMode ? themes.dark : themes.light;

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    // Clean reset - only clear what's necessary
    setUploadedFile(file);
    setOriginalImage(URL.createObjectURL(file));
    setUploadedZipFile(null);
    
    // Clear animation state only
    setPlacementData(null);
    setIsAnimating(false);
    setScatteredPieces([]);
    setAnimationPhase('scattered');
    animationRef.current = [];
    currentPlacementDataRef.current = null;
    
    // Reset other state
    setShattered(false);
    setShuffledPieces([]);
    setError(null);
    setRebuiltUrl(null);
    setRebuildRuntime(null);
    setRebuildTimingBreakdown(null);
    setShatterRuntime(null);
    setTimingBreakdown(null);
    setCurrentPieceIndex(0);
  };

  const handleZipUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploadedZipFile(file);
    setUploadedFile(null);
    setOriginalImage(null);
    resetState();
  };

  const resetState = () => {
    setShattered(false);
    setShuffledPieces([]);
    setError(null);
    setLoading(false);
    setShowGame(false);
    setShatterRuntime(null);
    setTimingBreakdown(null);
    setRebuiltUrl(null);
    setRebuildRuntime(null);
    setRebuildTimingBreakdown(null);
    setPlacementData(null);
    setIsAnimating(false);
    setScatteredPieces([]);
    setAnimationPhase('scattered');
    setCurrentPieceIndex(0);
    currentPlacementDataRef.current = null;
  };

  const handleShatter = async () => {
    if (!uploadedFile) {
      setError('Please upload an image first');
      return;
    }
    setLoading(true);
    setShowGame(true);
    setError(null);
    setRebuiltUrl(null);
    setShatterRuntime(null);
    setTimingBreakdown(null);
    try {
      const formData = new FormData();
      formData.append('image', uploadedFile);
      formData.append('piece_count', pieceCount.toString());
      const res = await fetch(`${API_URL}/shatter`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.pieces && data.pieces.length === pieceCount) {
        setPieces(data.pieces);
        setShuffledPieces(data.pieces);
        setOriginalImageSize(data.image_size);
        setShattered(true);
        setShatterRuntime(data.runtime ?? null);
        setTimingBreakdown(data.timing_breakdown ?? null);
      } else if (data.pieces) {
        setError(`Expected ${pieceCount} pieces, got ${data.pieces.length}. Try again.`);
      } else {
        setError(data.error || 'Failed to shatter image');
      }
    } catch (err) {
      setError('Failed to connect to backend');
    }
    setLoading(false);
    setShowGame(false);
  };

  const handleLoadZipPieces = async () => {
    if (!uploadedZipFile) {
      setError('Please upload a zip file first');
      return;
    }
    setLoading(true);
    setShowGame(true);
    setError(null);
    setRebuiltUrl(null);
    setRebuildRuntime(null);
    setRebuildTimingBreakdown(null);
    try {
      const formData = new FormData();
      formData.append('zip_file', uploadedZipFile);
      formData.append('piece_count', pieceCount.toString());
      const res = await fetch(`${API_URL}/load_zip_pieces`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.pieces && data.pieces.length === pieceCount) {
        setPieces(data.pieces);
        setShuffledPieces(data.pieces);
        setShattered(true);
        setRebuildRuntime(data.runtime ?? null);
        setRebuildTimingBreakdown(data.timing_breakdown ?? null);
      } else if (data.pieces) {
        setError(`Expected ${pieceCount} pieces, got ${data.pieces.length}. Check your zip file.`);
      } else {
        setError(data.error || 'Failed to load pieces from zip');
      }
    } catch (err) {
      setError('Failed to connect to backend');
    }
    setLoading(false);
    setShowGame(false);
  };

  const handleShuffle = async () => {
    try {
      // Call server endpoint to shuffle the pieces folder
      await fetch('http://127.0.0.1:5001/shuffle_pieces', { method: 'POST' });
  
      // After shuffling on server, fetch updated pieces list
      const res = await fetch('http://127.0.0.1:5001/load_pieces'); // You can make a simple endpoint that lists pieces
      const data = await res.json();
      setShuffledPieces(data.pieces);
      setRebuiltUrl(null);
    } catch (err) {
      console.error('Error shuffling pieces:', err);
    }
  };

  const handleRebuild = async () => {
    setLoading(true);
    setShowGame(true);
    setError(null);
    setRebuiltUrl(null);
    setRebuildRuntime(null);
    setRebuildTimingBreakdown(null);
    
    // Clean animation reset
    setPlacementData(null);
    setIsAnimating(false);
    setScatteredPieces([]);
    setAnimationPhase('scattered');
    animationRef.current = [];
    currentPlacementDataRef.current = null;
    
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
        setRebuildTimingBreakdown(data.timing_breakdown ?? null);
        
        // Set fresh placement data
        setPlacementData(data.placement_data ?? null);
        
        // Start animation after a short delay
        setTimeout(() => {
          startAnimation();
        }, 100);
      } else {
        setError(data.error || 'Failed to rebuild image');
      }
    } catch (err) {
      setError('Failed to connect to backend');
    }
    setLoading(false);
    setShowGame(false);
  };

  const handleReset = () => {
    resetState();
    setUploadedFile(null);
    setUploadedZipFile(null);
    setOriginalImage(null);
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

  const getPieceSrc = (piece: string) => `${API_URL}${piece}?t=${Date.now()}`;

  const generateScatteredPositions = (placementData: any) => {
    const { canvas_size, piece_size } = placementData;
    const scattered = placementData.pieces.map((piece: any) => {
      // Generate random scattered positions around the canvas
      const margin = 100;
      const x = Math.random() * (canvas_size.width + margin * 2) - margin;
      const y = Math.random() * (canvas_size.height + margin * 2) - margin;
      
      return {
        ...piece,
        scattered_position: [x, y],
        current_position: [x, y]
      };
    });
    return scattered;
  };

  const startAnimation = () => {
    if (!placementData) return;
    
    // Clean animation start
    animationRef.current = [];
    animationIdRef.current += 1;
    const currentAnimationId = animationIdRef.current;
    
    // Store current placement data
    currentPlacementDataRef.current = placementData;
    
    setIsAnimating(true);
    setAnimationPhase('scattered');
    
    const scattered = generateScatteredPositions(currentPlacementDataRef.current);
    setScatteredPieces(scattered);
    
    // Start animation immediately
    setAnimationPhase('moving');
    
    // Animate pieces to the center (overlay position)
    const animationDuration = 2000; // 2 seconds
    const startTime = performance.now();
    
    const animate = (currentTime: number) => {
      // Check if this animation is still valid
      if (currentAnimationId !== animationIdRef.current) {
        return;
      }
      
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / animationDuration, 1);
      
      // Smoother easing function
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      
      const updatedPieces = scattered.map((piece: any) => {
        const [startX, startY] = piece.scattered_position;
        const [endX, endY] = piece.final_position;
        
        // All pieces move to center (0,0) for overlay
        const currentX = startX + (0 - startX) * easeOutCubic;
        const currentY = startY + (0 - startY) * easeOutCubic;
        
        return {
          ...piece,
          current_position: [currentX, currentY]
        };
      });
      
      // Store current positions in ref for smooth rendering
      animationRef.current = updatedPieces;
      
      // Update state less frequently to reduce jitter
      if (Math.floor(progress * 120) % 3 === 0) {
        setScatteredPieces([...updatedPieces]);
      }
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        // Animation complete
        setAnimationPhase('complete');
        setScatteredPieces(updatedPieces);
      }
    };
    
    requestAnimationFrame(animate);
  };

  const closeAnimation = () => {
    // Clean animation close - but keep placement data for replay
    setIsAnimating(false);
    setScatteredPieces([]);
    setAnimationPhase('scattered');
    
    // Don't clear placement data - keep it for replay
    // setPlacementData(null);
    
    // Clear refs
    animationRef.current = [];
    currentPlacementDataRef.current = null;
  };

  const nextPiece = () => {
    setCurrentPieceIndex((prev) => (prev + 1) % shuffledPieces.length);
  };

  const prevPiece = () => {
    setCurrentPieceIndex((prev) => (prev - 1 + shuffledPieces.length) % shuffledPieces.length);
  };

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (!shattered) return;
      switch (e.key) {
        case 'ArrowRight':
        case ' ':
          e.preventDefault();
          nextPiece();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          prevPiece();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [shuffledPieces.length, shattered]);

  // Cleanup animation ref when component unmounts or animation state changes
  useEffect(() => {
    return () => {
      animationRef.current = [];
      currentPlacementDataRef.current = null;
    };
  }, [isAnimating]);

  // Additional cleanup when placement data changes
  useEffect(() => {
    if (!placementData) {
      // Clear animation state when placement data is cleared
      setIsAnimating(false);
      setScatteredPieces([]);
      setAnimationPhase('scattered');
      animationRef.current = [];
      currentPlacementDataRef.current = null;
    }
  }, [placementData]);

  return (
    <div className="App" style={{ 
      minHeight: '100vh',
      backgroundColor: theme.background,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      color: theme.text,
      transition: 'all 0.3s ease'
    }}>
      {showGame && <LoadingGame theme={theme} />}
      {/* Header - Fixed Position */}
      <header style={{
        backgroundColor: theme.surface,
        borderBottom: `1px solid ${theme.border}`,
        padding: '20px 0',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: theme.shadow
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ 
            color: theme.text, 
            margin: 0, 
            fontSize: '28px',
            fontWeight: '600'
          }}>
            🧩 Image Shatter & Rebuild
          </h1>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              style={{
                backgroundColor: sidebarOpen ? theme.primary : theme.surfaceHover,
                border: `1px solid ${theme.border}`,
                borderRadius: '8px',
                padding: '8px 12px',
                cursor: 'pointer',
                color: sidebarOpen ? 'white' : theme.text,
                fontSize: '14px',
                transition: 'all 0.2s ease'
              }}
            >
              📊 Stats
            </button>
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              style={{
                backgroundColor: theme.surfaceHover,
                border: `1px solid ${theme.border}`,
                borderRadius: '8px',
                padding: '8px 12px',
                cursor: 'pointer',
                color: theme.text,
                fontSize: '14px',
                transition: 'all 0.2s ease'
              }}
            >
              {isDarkMode ? '☀️ Light' : '🌙 Dark'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '40px 20px',
        minHeight: 'calc(100vh - 100px)'
      }}>
        {/* Upload Section - Fixed Height */}
        <div style={{
          backgroundColor: theme.surface,
          borderRadius: '16px',
          padding: '30px',
          marginBottom: '30px',
          boxShadow: theme.shadow,
          minHeight: '200px',
          border: `1px solid ${theme.border}`
        }}>
          <h2 style={{ 
            color: theme.text, 
            margin: '0 0 20px 0',
            fontSize: '20px',
            fontWeight: '500'
          }}>
            Upload Image or Pieces
          </h2>
          
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
            {/* Image Upload */}
            <div style={{ flex: '1', minWidth: '300px' }}>
              <h3 style={{ 
                color: theme.textSecondary, 
                margin: '0 0 15px 0',
                fontSize: '16px',
                fontWeight: '500'
              }}>
                Shatter New Image
              </h3>
              <input 
                type="file" 
                accept="image/png,image/jpeg" 
                onChange={handleImageUpload}
                style={{ 
                  width: '100%',
                  padding: '12px',
                  border: `2px dashed ${theme.border}`,
                  borderRadius: '12px',
                  backgroundColor: theme.background,
                  cursor: 'pointer',
                  color: theme.text,
                  transition: 'all 0.2s ease'
                }}
              />

              {originalImage && (
                <div style={{ marginTop: '15px', textAlign: 'center' }}>
          <img
            src={originalImage}
            alt="Original"
                    style={{ 
                      maxWidth: '100%', 
                      maxHeight: '150px',
                      border: `2px solid ${theme.border}`, 
                      borderRadius: '12px',
                      display: 'block',
                      margin: '0 auto'
                    }}
          />
          <button
            onClick={handleShatter}
                    disabled={loading}
            style={{
                      backgroundColor: theme.primary,
              color: 'white',
              border: 'none',
                      padding: '12px 24px',
                      borderRadius: '12px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      fontWeight: '600',
                      fontSize: '14px',
                      marginTop: '10px',
                      opacity: loading ? 0.6 : 1,
                      transition: 'all 0.2s ease',
                      boxShadow: theme.shadow
                    }}
                    onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = theme.primaryHover)}
                    onMouseLeave={(e) => !loading && (e.currentTarget.style.backgroundColor = theme.primary)}
                  >
                    {loading ? 'Processing...' : 'Shatter Image'}
                  </button>
                </div>
              )}
            </div>

            {/* Zip Upload */}
            <div style={{ flex: '1', minWidth: '300px' }}>
              <h3 style={{ 
                color: theme.textSecondary, 
                margin: '0 0 15px 0',
                fontSize: '16px',
                fontWeight: '500'
              }}>
                Load Existing Pieces
              </h3>
              <input 
                type="file" 
                accept=".zip" 
                onChange={handleZipUpload}
                style={{ 
                  width: '100%',
                  padding: '12px',
                  border: `2px dashed ${theme.border}`,
                  borderRadius: '12px',
                  backgroundColor: theme.background,
              cursor: 'pointer',
                  color: theme.text,
                  transition: 'all 0.2s ease'
                }}
              />
              <div style={{ marginTop: '15px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '8px',
                  fontSize: '14px',
                  color: theme.textSecondary
                }}>
                  Number of pieces:
                </label>
                <input
                  type="number"
                  value={pieceCount}
                  min="1"
                  max="100"
                  style={{
                    width: '100px',
                    padding: '8px 12px',
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    fontSize: '14px',
                    backgroundColor: theme.background,
                    color: theme.text
                  }}
                />
                {uploadedZipFile && (
                  <button
                    onClick={handleLoadZipPieces}
                    disabled={loading}
                    style={{
                      backgroundColor: theme.accent,
                      color: 'white',
                      border: 'none',
                      padding: '12px 24px',
                      borderRadius: '12px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      fontWeight: '600',
                      fontSize: '14px',
                      marginTop: '10px',
                      marginLeft: '10px',
                      opacity: loading ? 0.6 : 1,
                      transition: 'all 0.2s ease',
                      boxShadow: theme.shadow
                    }}
                  >
                    {loading ? 'Loading...' : 'Load Pieces'}
          </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div style={{
            backgroundColor: isDarkMode ? '#7f1d1d' : '#fef2f2',
            color: isDarkMode ? '#fca5a5' : '#dc2626',
            padding: '15px',
            borderRadius: '12px',
            marginBottom: '20px',
            border: `1px solid ${isDarkMode ? '#991b1b' : '#fecaca'}`
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Piece Browser - Only show when shattered */}
        {shattered && shuffledPieces.length > 0 && (
            <div style={{
            backgroundColor: theme.surface,
            borderRadius: '16px',
            padding: '30px',
            marginBottom: '30px',
            boxShadow: theme.shadow,
            border: `1px solid ${theme.border}`
          }}>
            <div style={{ 
              display: 'flex',
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '25px',
              flexWrap: 'wrap',
              gap: '10px'
            }}>
              <h2 style={{ 
                color: theme.text, 
                margin: 0,
                fontSize: '20px',
                fontWeight: '500'
              }}>
                Piece Browser ({shuffledPieces.length} pieces)
              </h2>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                <button 
                  onClick={handleShuffle}
                  style={{
                    backgroundColor: theme.secondary,
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                    transition: 'all 0.2s ease'
                  }}
                >
                  Shuffle
                </button>
                <button 
                  onClick={handleRebuild}
                  disabled={loading}
                  style={{
                    backgroundColor: theme.primary,
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                    opacity: loading ? 0.6 : 1,
                    transition: 'all 0.2s ease'
                  }}
                >
                  {loading ? 'Rebuilding...' : 'Rebuild'}
                </button>
                <button 
                  onClick={handleDownloadPieces}
                  style={{
                    backgroundColor: theme.accent,
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                    transition: 'all 0.2s ease'
                  }}
                >
                  Download
                </button>
                <button 
                  onClick={handleReset}
                  style={{
                    backgroundColor: theme.danger,
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                    transition: 'all 0.2s ease'
                  }}
                >
                  Reset
                </button>
              </div>
          </div>

            {/* Carousel */}
                  <div style={{
                    position: 'relative',
              width: '100%',
              height: '350px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '30px',
              marginBottom: '20px'
            }}>
              {/* Previous Piece */}
              <div style={{
                width: '140px',
                height: '140px',
                border: `2px solid ${theme.border}`,
                borderRadius: '16px',
                overflow: 'hidden',
                opacity: 0.7,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                backgroundColor: theme.background
              }} 
              onClick={prevPiece}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '0.7'}
              >
                <img
                  src={getPieceSrc(shuffledPieces[(currentPieceIndex - 1 + shuffledPieces.length) % shuffledPieces.length])}
                  alt={`piece-${(currentPieceIndex - 1 + shuffledPieces.length) % shuffledPieces.length}`}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                    objectPosition: 'center'
                  }}
                />
              </div>

              {/* Current Piece */}
                  <div style={{
                width: '320px',
                height: '320px',
                border: `3px solid ${theme.primary}`,
                borderRadius: '16px',
                overflow: 'hidden',
                    position: 'relative',
                backgroundColor: theme.background,
                boxShadow: theme.shadowLarge
              }}>
                <img
                  src={getPieceSrc(shuffledPieces[currentPieceIndex])}
                  alt={`piece-${currentPieceIndex}`}
                          style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                            objectPosition: 'center',
                    display: 'block'
                  }}
                />
                <div style={{
                  position: 'absolute',
                  bottom: '15px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: 'rgba(0,0,0,0.8)',
                  color: 'white',
                  padding: '8px 16px',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: '600',
                  zIndex: 10
                }}>
                  {currentPieceIndex + 1} / {shuffledPieces.length}
                  </div>
                </div>

              {/* Next Piece */}
              <div style={{
                width: '140px',
                height: '140px',
                border: `2px solid ${theme.border}`,
                borderRadius: '16px',
                overflow: 'hidden',
                opacity: 0.7,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                backgroundColor: theme.background
              }} 
              onClick={nextPiece}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '0.7'}
              >
                <img
                  src={getPieceSrc(shuffledPieces[(currentPieceIndex + 1) % shuffledPieces.length])}
                  alt={`piece-${(currentPieceIndex + 1) % shuffledPieces.length}`}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                    objectPosition: 'center'
                  }}
                />
                </div>

              {/* Navigation Controls */}
              <div style={{
                position: 'absolute',
                top: '50%',
                left: 0,
                right: 0,
                transform: 'translateY(-50%)',
                display: 'flex',
                justifyContent: 'space-between',
                padding: '0 30px',
                pointerEvents: 'none'
              }}>
                <button 
                  onClick={prevPiece} 
            style={{
                    background: 'rgba(0,0,0,0.6)', 
                    border: 'none', 
                    borderRadius: '50%', 
                    width: '50px',
                    height: '50px',
                    cursor: 'pointer',
                    color: 'white',
                    fontSize: '20px',
                    pointerEvents: 'auto',
                    display: 'flex',
                    alignItems: 'center',
              justifyContent: 'center',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0,0,0,0.8)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(0,0,0,0.6)'}
                >
                  ←
                </button>
                <button 
                  onClick={nextPiece} 
                style={{
                    background: 'rgba(0,0,0,0.6)', 
                    border: 'none', 
                    borderRadius: '50%', 
                    width: '50px',
                    height: '50px',
                  cursor: 'pointer',
                    color: 'white',
                    fontSize: '20px',
                    pointerEvents: 'auto',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0,0,0,0.8)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(0,0,0,0.6)'}
                >
                  →
                </button>
              </div>
          </div>

            <p style={{ 
              textAlign: 'center', 
              fontSize: '14px', 
              color: theme.textMuted,
              margin: 0
            }}>
              Use arrow keys or click to navigate • Space to advance
            </p>

            {/* Theme Toggle Hint */}
            <div style={{
              marginTop: '15px',
              padding: '12px 16px',
              backgroundColor: theme.surfaceHover,
              borderRadius: '12px',
              border: `1px solid ${theme.border}`,
              textAlign: 'center'
            }}>
              <p style={{
                margin: 0,
                fontSize: '13px',
                color: theme.textSecondary,
                lineHeight: '1.4'
              }}>
                💡 <strong>Tip:</strong> If pieces appear invisible, try toggling between light and dark mode in the header. 
                Some pieces may blend with the current background.
              </p>
            </div>
          </div>
        )}

        {/* Rebuilt Image */}
          {rebuiltUrl && (
          <div style={{
            backgroundColor: theme.surface,
            borderRadius: '16px',
            padding: '30px',
            boxShadow: theme.shadow,
            border: `1px solid ${theme.border}`
          }}>
            <h2 style={{ 
              color: theme.text, 
              margin: '0 0 20px 0',
              fontSize: '20px',
              fontWeight: '500'
            }}>
              Rebuilt Image
            </h2>
            <div style={{ textAlign: 'center' }}>
              <img
                src={rebuiltUrl + '?t=' + Date.now()}
                alt="rebuilt"
                style={{ 
                  maxWidth: '100%', 
                  maxHeight: '500px',
                  border: `2px solid ${theme.border}`,
                  borderRadius: '12px',
                  boxShadow: theme.shadow
                }}
              />
            </div>
            
            {/* Replay Animation Button */}
            {placementData && (
              <div style={{ textAlign: 'center', marginTop: '20px' }}>
                <button
                  onClick={startAnimation}
                  disabled={isAnimating}
                  style={{
                    backgroundColor: theme.primary,
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '10px 20px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: isAnimating ? 'not-allowed' : 'pointer',
                    opacity: isAnimating ? 0.6 : 1,
                    transition: 'all 0.2s ease'
                  }}
                >
                  {isAnimating ? '🔄 Animating...' : '🎬 Replay Animation'}
                </button>
              </div>
              )}
            </div>
      )}

        {/* Animation Overlay */}
        {isAnimating && scatteredPieces.length > 0 && (
        <div
            key={`animation-${animationIdRef.current}`} // Use animation ID for proper re-render
          style={{
            position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.9)',
              zIndex: 2000,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
              overflow: 'hidden'
            }}
            onClick={closeAnimation} // Click outside to close
          >
            <div 
              style={{
                position: 'relative',
                width: '800px',
                height: '600px',
                border: '2px solid #fff',
                borderRadius: '8px',
                backgroundColor: '#000',
                overflow: 'hidden'
              }}
              onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
            >
              {scatteredPieces.map((piece: any, index: number) => {
                // Use ref for most current positions during animation
                const currentPiece = animationRef.current[index] || piece;
                const [x, y] = currentPiece.current_position;
                
                // Add cache-busting to prevent stale images
                const pieceUrl = `${API_URL}/static/pieces/${piece.filename}?t=${Date.now()}&id=${animationIdRef.current}`;
                
                // Use the placement data that was current when animation started
                const currentPlacementData = currentPlacementDataRef.current || placementData;
                if (!currentPlacementData) return null;
                
                // Calculate scale factor to fit the canvas within the animation box
                const canvasWidth = currentPlacementData?.canvas_size?.width || 800;
                const canvasHeight = currentPlacementData?.canvas_size?.height || 600;
                const scaleX = 800 / canvasWidth;
                const scaleY = 600 / canvasHeight;
                const scale = Math.min(scaleX, scaleY, 1); // Don't scale up, only down
                
                // Scale the piece size and positions
                const scaledPieceWidth = (currentPlacementData?.piece_size?.width || 100) * scale;
                const scaledPieceHeight = (currentPlacementData?.piece_size?.height || 100) * scale;
                const scaledX = x * scale;
                const scaledY = y * scale;
                
                return (
                  <img
                    key={`${piece.piece_index}-${animationIdRef.current}`} // Unique key for each piece and animation
                    src={pieceUrl}
                    alt={`Piece ${piece.piece_index}`}
            style={{
                      position: 'absolute',
                      left: scaledX + 400, // Center in 800px box
                      top: scaledY + 300,  // Center in 600px box
                      width: scaledPieceWidth,
                      height: scaledPieceHeight,
                      transform: 'translate(-50%, -50%)',
                      pointerEvents: 'none'
                    }}
                  />
                );
              })}
              
              {/* Exit Button */}
              <button
                onClick={closeAnimation}
                style={{
                  position: 'absolute',
                  top: '15px',
                  right: '15px',
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '50%',
                  width: '40px',
                  height: '40px',
                  cursor: 'pointer',
                  color: '#fff',
                  fontSize: '18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease',
                  zIndex: 10
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.5)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                }}
              >
                ✕
              </button>
              
              {/* Animation Progress Bar */}
              {animationPhase === 'moving' && (
                <div style={{
                  position: 'absolute',
                  bottom: '20px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: '200px',
                  height: '4px',
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  borderRadius: '2px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: '100%',
                    height: '100%',
                    backgroundColor: '#fff',
                    borderRadius: '2px',
                    animation: 'progress 2s linear'
                  }} />
        </div>
      )}

              {/* Animation Text */}
              <div style={{
                position: 'absolute',
                top: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                color: '#fff',
                fontSize: '18px',
                fontWeight: '500',
                textAlign: 'center'
              }}>
                {animationPhase === 'scattered' && '🧩 Pieces Scattered - Animation Starting Soon...'}
                {animationPhase === 'moving' && '🧩 Reconstructing Puzzle...'}
                {animationPhase === 'complete' && '✅ Puzzle Reconstructed! Click ✕ to exit'}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Toggleable Sidebar for Timing Stats */}
      {(shatterRuntime !== null || rebuildRuntime !== null || timingBreakdown || rebuildTimingBreakdown) && (
        <>
          {/* Side Panel */}
          <div style={{
            position: 'fixed',
            top: '20px',
            right: sidebarOpen ? '20px' : '-100%',
            width: '300px',
            maxHeight: 'calc(100vh - 40px)',
            overflowY: 'auto',
            backgroundColor: theme.surface,
            borderRadius: '12px',
            padding: '20px',
            textAlign: 'left',
            border: `1px solid ${theme.border}`,
            boxShadow: theme.shadowLarge,
            zIndex: 1000,
            transition: 'right 0.3s ease',
            opacity: sidebarOpen ? 1 : 0,
            visibility: sidebarOpen ? 'visible' : 'hidden'
          }}>
            <h3 style={{ 
              margin: '0 0 20px 0', 
              color: theme.text, 
              borderBottom: `2px solid ${theme.primary}`, 
              paddingBottom: '10px',
              fontSize: '16px',
              fontWeight: '600'
            }}>
              Performance Analytics
            </h3>
            
            {shatterRuntime !== null && (
              <div style={{ 
                marginBottom: '20px', 
                padding: '15px', 
                backgroundColor: theme.background, 
                borderRadius: '8px', 
                border: `1px solid ${theme.border}`
              }}>
                <h4 style={{ 
                  margin: '0 0 10px 0', 
                  fontSize: '14px', 
                  color: theme.text,
                  fontWeight: '600'
                }}>
                  Shatter Performance
                </h4>
                <div style={{
                  fontSize: '20px',
                  fontWeight: 'bold',
                  color: theme.primary,
                  marginBottom: '10px',
                  textAlign: 'center'
                }}>
                  {shatterRuntime.toFixed(2)}s
                </div>
                {timingBreakdown && (
                  <div style={{ fontSize: '12px', color: theme.textSecondary }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0',
                      borderBottom: `1px solid ${theme.border}`
                    }}>
                      <span>Upload:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{timingBreakdown.upload?.toFixed(3)}s</span>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0',
                      borderBottom: `1px solid ${theme.border}`
                    }}>
                      <span>Cleanup:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{timingBreakdown.cleanup?.toFixed(3)}s</span>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0',
                      borderBottom: `1px solid ${theme.border}`
                    }}>
                      <span>Shatter:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{timingBreakdown.shatter?.toFixed(3)}s</span>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0'
                    }}>
                      <span>Response:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{timingBreakdown.response?.toFixed(3)}s</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {rebuildRuntime !== null && (
              <div style={{ 
                marginBottom: '20px', 
                padding: '15px', 
                backgroundColor: theme.background, 
                borderRadius: '8px', 
                border: `1px solid ${theme.border}`
              }}>
                <h4 style={{ 
                  margin: '0 0 10px 0', 
                  fontSize: '14px', 
                  color: theme.text,
                  fontWeight: '600'
                }}>
                  Rebuild Performance
                </h4>
                <div style={{
                  fontSize: '20px',
                  fontWeight: 'bold',
                  color: theme.primary,
                  marginBottom: '10px',
                  textAlign: 'center'
                }}>
                  {rebuildRuntime.toFixed(2)}s
                </div>
                {rebuildTimingBreakdown && (
                  <div style={{ fontSize: '12px', color: theme.textSecondary }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0',
                      borderBottom: `1px solid ${theme.border}`
                    }}>
                      <span>Copy:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{rebuildTimingBreakdown.copy?.toFixed(3)}s</span>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0',
                      borderBottom: `1px solid ${theme.border}`
                    }}>
                      <span>Load:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{rebuildTimingBreakdown.load?.toFixed(3)}s</span>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0',
                      borderBottom: `1px solid ${theme.border}`
                    }}>
                      <span>Reconstruct:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{rebuildTimingBreakdown.reconstruct?.toFixed(3)}s</span>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0',
                      borderBottom: `1px solid ${theme.border}`
                    }}>
                      <span>Assemble:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{rebuildTimingBreakdown.assemble?.toFixed(3)}s</span>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '4px 0'
                    }}>
                      <span>Cleanup:</span>
                      <span style={{ fontWeight: '600', color: theme.text }}>{rebuildTimingBreakdown.cleanup?.toFixed(3)}s</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Summary Stats */}
            {(shatterRuntime !== null || rebuildRuntime !== null) && (
              <div style={{
                padding: '12px',
                backgroundColor: theme.primary,
                color: 'white',
                borderRadius: '8px',
                textAlign: 'center',
                marginTop: '15px'
              }}>
                <div style={{ fontSize: '12px', marginBottom: '3px', opacity: 0.9 }}>
                  Total Time
                </div>
                <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                  {((shatterRuntime || 0) + (rebuildRuntime || 0)).toFixed(2)}s
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* Loading Overlay - Only show when not playing game */}
      {loading && !showGame && (
        <div style={{
            position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          zIndex: 2000
        }}>
          <div style={{
            backgroundColor: theme.surface,
            padding: '30px 40px',
            borderRadius: '16px',
            textAlign: 'center',
            boxShadow: theme.shadowLarge,
            border: `1px solid ${theme.border}`
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid theme.border',
              borderTop: `4px solid ${theme.primary}`,
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 15px auto'
            }}></div>
            <p style={{ margin: 0, fontSize: '16px', color: theme.text }}>Processing...</p>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default App;
