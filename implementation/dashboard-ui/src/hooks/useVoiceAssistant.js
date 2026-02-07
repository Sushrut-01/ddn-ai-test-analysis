import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * JARVIS-Style Voice Assistant Hook
 * Implements real voice interaction using Web Speech API
 *
 * Features:
 * - Speech Recognition (listening to user)
 * - Speech Synthesis (JARVIS speaks)
 * - Wake word detection ("Hey JARVIS")
 * - Continuous conversation mode
 * - Voice command processing
 */
export const useVoiceAssistant = (options = {}) => {
  const {
    autoStart = false,
    language = 'en-US',
    jarvisVoice = 'Google UK English Male', // British accent like JARVIS
    continuousMode = false,
    wakeWord = 'hey jarvis',
    onCommand = null
  } = options;

  // State
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const [error, setError] = useState(null);
  const [isWakeWordMode, setIsWakeWordMode] = useState(false);

  // Refs
  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);
  const voicesRef = useRef([]);

  // Check browser support
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const SpeechSynthesis = window.speechSynthesis;

    if (!SpeechRecognition || !SpeechSynthesis) {
      setIsSupported(false);
      setError('Voice features not supported in this browser. Please use Chrome, Edge, or Safari.');
      console.error('Web Speech API not supported');
      return;
    }

    // Initialize speech recognition
    const recognition = new SpeechRecognition();
    recognition.continuous = continuousMode;
    recognition.interimResults = true;
    recognition.lang = language;
    recognition.maxAlternatives = 1;

    // Event handlers
    recognition.onstart = () => {
      console.log('🎤 JARVIS: Listening...');
      setIsListening(true);
      setError(null);
    };

    recognition.onend = () => {
      console.log('🎤 JARVIS: Stopped listening');
      setIsListening(false);

      // Auto-restart in wake word mode
      if (isWakeWordMode && recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (err) {
          console.warn('Recognition restart failed:', err);
        }
      }
    };

    recognition.onerror = (event) => {
      console.error('🎤 JARVIS: Speech recognition error:', event.error);

      if (event.error === 'no-speech') {
        setError('No speech detected. Please try again.');
      } else if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone access.');
      } else {
        setError(`Voice error: ${event.error}`);
      }

      setIsListening(false);
    };

    recognition.onresult = (event) => {
      const last = event.results.length - 1;
      const text = event.results[last][0].transcript.toLowerCase().trim();
      const confidence = event.results[last][0].confidence;
      const isFinal = event.results[last].isFinal;

      console.log(`🎤 Heard: "${text}" (${(confidence * 100).toFixed(1)}% confidence)`);

      setTranscript(text);

      // Check for wake word
      if (isWakeWordMode && text.includes(wakeWord)) {
        console.log('🎙️ Wake word detected!');
        speak('Yes sir, I am here. How may I assist you?');
        setIsWakeWordMode(false);
        return;
      }

      // Process command if final result
      if (isFinal && onCommand) {
        onCommand(text, confidence);
      }
    };

    recognitionRef.current = recognition;

    // Load available voices
    const loadVoices = () => {
      voicesRef.current = synthRef.current.getVoices();
      console.log('🔊 Available voices:', voicesRef.current.length);
    };

    loadVoices();
    if (synthRef.current.onvoiceschanged !== undefined) {
      synthRef.current.onvoiceschanged = loadVoices;
    }

    // Auto-start if requested
    if (autoStart) {
      startListening();
    }

    // Cleanup
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, [language, continuousMode, autoStart]);

  /**
   * Start listening for voice input
   */
  const startListening = useCallback(() => {
    if (!recognitionRef.current) {
      setError('Speech recognition not initialized');
      return;
    }

    try {
      recognitionRef.current.start();
    } catch (err) {
      if (err.name === 'InvalidStateError') {
        console.log('Recognition already started');
      } else {
        console.error('Start listening error:', err);
        setError('Failed to start listening');
      }
    }
  }, []);

  /**
   * Stop listening
   */
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      setIsWakeWordMode(false);
      recognitionRef.current.stop();
    }
  }, []);

  /**
   * JARVIS speaks (Text-to-Speech)
   */
  const speak = useCallback((text, options = {}) => {
    if (!synthRef.current) {
      console.error('Speech synthesis not available');
      return Promise.reject(new Error('Speech synthesis not available'));
    }

    return new Promise((resolve, reject) => {
      // Cancel any ongoing speech
      synthRef.current.cancel();

      const utterance = new SpeechSynthesisUtterance(text);

      // Load voices if not loaded
      if (voicesRef.current.length === 0) {
        voicesRef.current = synthRef.current.getVoices();
        console.log('🔊 Loaded voices:', voicesRef.current.map(v => v.name));
      }

      // Find JARVIS-like voice (British male)
      let voice = voicesRef.current.find(v =>
        v.name.includes('Google UK English Male') ||
        v.name.includes('Daniel') || // British on Mac
        v.name.includes('British') ||
        v.name.includes('Male')
      );

      // Fallback to any English male voice
      if (!voice) {
        voice = voicesRef.current.find(v =>
          v.lang.startsWith('en')
        );
      }

      if (voice) {
        utterance.voice = voice;
        console.log('🔊 Using voice:', voice.name);
      } else {
        console.warn('🔊 No specific voice found, using default');
      }

      // Voice characteristics (JARVIS-like)
      utterance.rate = options.rate || 1.0; // Normal speed
      utterance.pitch = options.pitch || 1.0; // Normal pitch
      utterance.volume = options.volume || 1.0; // Full volume
      utterance.lang = options.lang || 'en-US'; // US English (more compatible)

      utterance.onstart = () => {
        console.log('🔊 JARVIS speaking:', text);
        setIsSpeaking(true);
      };

      utterance.onend = () => {
        console.log('🔊 JARVIS finished speaking');
        setIsSpeaking(false);
        resolve();
      };

      utterance.onerror = (event) => {
        console.error('🔊 Speech synthesis error:', event);
        setIsSpeaking(false);
        reject(event.error);
      };

      // Force speech to start
      console.log('🔊 Attempting to speak...');
      synthRef.current.speak(utterance);
    });
  }, []);

  /**
   * Stop JARVIS from speaking
   */
  const stopSpeaking = useCallback(() => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  }, []);

  /**
   * Enable wake word detection mode
   * JARVIS continuously listens for "Hey JARVIS"
   */
  const enableWakeWord = useCallback(() => {
    console.log('🎙️ Wake word mode enabled. Say "Hey JARVIS" to activate.');
    setIsWakeWordMode(true);

    // Start continuous listening
    if (recognitionRef.current) {
      recognitionRef.current.continuous = true;
      startListening();
    }

    speak('Wake word detection enabled. Say "Hey JARVIS" when you need me, sir.');
  }, [startListening, speak]);

  /**
   * Disable wake word detection
   */
  const disableWakeWord = useCallback(() => {
    console.log('🎙️ Wake word mode disabled');
    setIsWakeWordMode(false);
    stopListening();
  }, [stopListening]);

  /**
   * Process voice command
   */
  const processCommand = useCallback((command) => {
    const cmd = command.toLowerCase().trim();

    console.log(`🎯 Processing command: "${cmd}"`);

    // Built-in commands
    if (cmd.includes('stop listening') || cmd.includes('stop')) {
      stopListening();
      speak('Listening stopped, sir.');
      return 'stop';
    }

    if (cmd.includes('hello') || cmd.includes('hi jarvis')) {
      speak('Hello sir. All systems operational.');
      return 'greeting';
    }

    if (cmd.includes('status')) {
      speak('All systems functioning normally, sir.');
      return 'status';
    }

    // Pass to custom handler
    if (onCommand) {
      onCommand(cmd);
    }

    return cmd;
  }, [stopListening, speak, onCommand]);

  return {
    // State
    isListening,
    isSpeaking,
    transcript,
    isSupported,
    error,
    isWakeWordMode,

    // Methods
    startListening,
    stopListening,
    speak,
    stopSpeaking,
    enableWakeWord,
    disableWakeWord,
    processCommand,

    // Utils
    isActive: isListening || isSpeaking
  };
};

export default useVoiceAssistant;
