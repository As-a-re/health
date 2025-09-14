"use client";

import { useState, useEffect, useCallback } from 'react';

// Import types from the global scope
type SpeechRecognition = {
  prototype: any;
  new (): any;
};

interface SpeechRecognitionEvent extends Event {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
      isFinal: boolean;
    };
    length: number;
  };
  resultIndex: number;
}

type SpeechSynthesis = typeof window.speechSynthesis;
type SpeechSynthesisUtterance = typeof window.SpeechSynthesisUtterance;

type SpeechRecognitionHook = {
  isListening: boolean;
  transcript: string;
  startListening: () => void;
  stopListening: () => void;
  speak: (text: string) => void;
  error: string | null;
};

export const useSpeech = (): SpeechRecognitionHook => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [recognition, setRecognition] = useState<InstanceType<SpeechRecognition> | null>(null);
  const [synth, setSynth] = useState<SpeechSynthesis | null>(null);

  useEffect(() => {
    // Initialize speech recognition and synthesis
    if (typeof window !== 'undefined') {
      // Set up speech recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;
        recognitionInstance.interimResults = true;
        recognitionInstance.lang = 'en-US';

        recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
          const results = Array.from(event.results);
          const transcript = results
            .map((result) => result[0]?.transcript || '')
            .join('');
          setTranscript(transcript);
        };

        recognitionInstance.onerror = (event: Event) => {
          console.error('Speech recognition error', event);
          setError('Speech recognition error occurred');
          setIsListening(false);
        };

        recognitionInstance.onend = () => {
          if (isListening) {
            recognitionInstance.start();
          }
        };

        setRecognition(recognitionInstance);
      } else {
        setError('Speech recognition not supported in this browser');
      }

      // Set up speech synthesis
      if ('speechSynthesis' in window) {
        setSynth(window.speechSynthesis);
      } else {
        setError('Speech synthesis not supported in this browser');
      }
    }

    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, [isListening]);

  const startListening = useCallback(() => {
    if (recognition) {
      try {
        recognition.start();
        setIsListening(true);
        setError(null);
      } catch (err) {
        console.error('Error starting speech recognition:', err);
        setError('Error starting speech recognition');
      }
    }
  }, [recognition]);

  const stopListening = useCallback(() => {
    if (recognition) {
      recognition.stop();
      setIsListening(false);
    }
  }, [recognition]);

  const speak = useCallback((text: string) => {
    if (synth) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      synth.speak(utterance);
    }
  }, [synth]);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    speak,
    error,
  };
};
