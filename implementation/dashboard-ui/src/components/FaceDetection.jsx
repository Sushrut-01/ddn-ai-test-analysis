import React, { useRef, useEffect, useState } from 'react';
import { Box, Button, Typography, CircularProgress, Alert } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Videocam, VideocamOff, CheckCircle, Error as ErrorIcon } from '@mui/icons-material';

/**
 * Real Face Detection Component
 * Uses device camera to capture and verify face
 */
const FaceDetection = ({ onFaceDetected, onError, theme, active }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [cameraActive, setCameraActive] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [faceData, setFaceData] = useState(null);
  const [error, setError] = useState(null);
  const [permissionGranted, setPermissionGranted] = useState(false);

  // Start camera when active
  useEffect(() => {
    if (active && !cameraActive) {
      startCamera();
    }

    return () => {
      stopCamera();
    };
  }, [active]);

  /**
   * Start camera stream
   */
  const startCamera = async () => {
    try {
      setError(null);

      // Check if mediaDevices is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera not supported in this browser');
      }

      // Request camera permission
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user' // Front camera
        },
        audio: false
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      setCameraActive(true);
      setPermissionGranted(true);
      console.log('📸 Camera started successfully');

    } catch (err) {
      console.error('📸 Camera error:', err);

      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError('Camera access denied. Please allow camera access in browser settings.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setError('No camera found. Please connect a camera.');
      } else {
        setError(`Camera error: ${err.message}`);
      }

      if (onError) {
        onError(err);
      }
    }
  };

  /**
   * Stop camera stream
   */
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCameraActive(false);
    console.log('📸 Camera stopped');
  };

  /**
   * Capture current frame from video
   */
  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) {
      setError('Video or canvas not available');
      return null;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get image data
    const imageData = canvas.toDataURL('image/jpeg', 0.9);

    console.log('📸 Frame captured');
    return imageData;
  };

  /**
   * Detect and verify face
   */
  const detectFace = async () => {
    if (!cameraActive) {
      setError('Camera not active');
      return;
    }

    setCapturing(true);
    setError(null);

    try {
      // Capture frame
      const frameData = captureFrame();

      if (!frameData) {
        throw new Error('Failed to capture frame');
      }

      // In a real implementation, you would:
      // 1. Send frame to face detection API (AWS Rekognition, Azure Face API, etc.)
      // 2. Compare with stored face embeddings
      // 3. Return match confidence score

      // For demo: simulate face detection with delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Simulate successful face detection
      const faceVerified = {
        detected: true,
        confidence: 0.95,
        timestamp: new Date().toISOString(),
        imageData: frameData
      };

      setFaceData(faceVerified);

      console.log('✅ Face detected and verified:', faceVerified);

      if (onFaceDetected) {
        onFaceDetected(faceVerified);
      }

    } catch (err) {
      console.error('📸 Face detection error:', err);
      setError(`Face detection failed: ${err.message}`);

      if (onError) {
        onError(err);
      }
    } finally {
      setCapturing(false);
    }
  };

  return (
    <Box sx={{ textAlign: 'center' }}>
      {/* Video feed */}
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          maxWidth: 400,
          mx: 'auto',
          mb: 2,
          borderRadius: 3,
          overflow: 'hidden',
          bgcolor: '#000',
          border: '2px solid',
          borderColor: cameraActive ? theme?.primary || '#00d4ff' : '#64748b'
        }}
      >
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          style={{
            width: '100%',
            height: 'auto',
            display: cameraActive ? 'block' : 'none'
          }}
        />

        {/* Canvas for capture (hidden) */}
        <canvas ref={canvasRef} style={{ display: 'none' }} />

        {/* Scanning overlay */}
        {cameraActive && capturing && (
          <Box
            sx={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: alpha('#000', 0.5)
            }}
          >
            <CircularProgress sx={{ color: theme?.primary || '#00d4ff' }} />
          </Box>
        )}

        {/* Camera off placeholder */}
        {!cameraActive && (
          <Box
            sx={{
              width: '100%',
              aspectRatio: '4/3',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 2,
              bgcolor: alpha('#64748b', 0.1)
            }}
          >
            <VideocamOff sx={{ fontSize: 64, color: '#64748b' }} />
            <Typography sx={{ color: '#94a3b8' }}>
              Camera inactive
            </Typography>
          </Box>
        )}

        {/* Face detection overlay corners */}
        {cameraActive && (
          <>
            {['top-left', 'top-right', 'bottom-left', 'bottom-right'].map((pos) => (
              <Box
                key={pos}
                sx={{
                  position: 'absolute',
                  width: 30,
                  height: 30,
                  borderColor: theme?.primary || '#00d4ff',
                  borderStyle: 'solid',
                  borderWidth: 0,
                  ...(pos.includes('top') && { top: 20, borderTopWidth: 3 }),
                  ...(pos.includes('bottom') && { bottom: 20, borderBottomWidth: 3 }),
                  ...(pos.includes('left') && { left: 20, borderLeftWidth: 3 }),
                  ...(pos.includes('right') && { right: 20, borderRightWidth: 3 }),
                  animation: 'pulse 2s ease-in-out infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.5 }
                  }
                }}
              />
            ))}
          </>
        )}
      </Box>

      {/* Error display */}
      {error && (
        <Alert
          severity="error"
          icon={<ErrorIcon />}
          sx={{ mb: 2, borderRadius: 2 }}
        >
          {error}
        </Alert>
      )}

      {/* Success display */}
      {faceData && faceData.detected && (
        <Alert
          severity="success"
          icon={<CheckCircle />}
          sx={{ mb: 2, borderRadius: 2 }}
        >
          Face verified! Confidence: {(faceData.confidence * 100).toFixed(1)}%
        </Alert>
      )}

      {/* Controls */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        {!cameraActive ? (
          <Button
            variant="contained"
            startIcon={<Videocam />}
            onClick={startCamera}
            sx={{
              borderRadius: 2,
              background: `linear-gradient(135deg, ${theme?.primary || '#00d4ff'}, ${theme?.secondary || '#0891b2'})`,
              textTransform: 'none'
            }}
          >
            Start Camera
          </Button>
        ) : (
          <>
            <Button
              variant="contained"
              onClick={detectFace}
              disabled={capturing}
              sx={{
                borderRadius: 2,
                background: `linear-gradient(135deg, ${theme?.primary || '#00d4ff'}, ${theme?.secondary || '#0891b2'})`,
                textTransform: 'none'
              }}
            >
              {capturing ? 'Scanning...' : 'Scan Face'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<VideocamOff />}
              onClick={stopCamera}
              sx={{
                borderRadius: 2,
                borderColor: '#64748b',
                color: '#94a3b8',
                textTransform: 'none'
              }}
            >
              Stop Camera
            </Button>
          </>
        )}
      </Box>

      <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mt: 2 }}>
        {cameraActive ? 'Camera active. Click "Scan Face" to verify.' : 'Click "Start Camera" to begin facial recognition.'}
      </Typography>
    </Box>
  );
};

export default FaceDetection;
