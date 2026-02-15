"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type RecordingState = "idle" | "recording" | "processing";

interface VoiceInputButtonProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  state?: RecordingState;
  className?: string;
  size?: "sm" | "lg";
}

export function VoiceInputButton({
  onRecordingComplete,
  state: externalState,
  className,
  size = "lg",
}: VoiceInputButtonProps) {
  const [internalState, setInternalState] = useState<RecordingState>("idle");
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const state = externalState ?? internalState;

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const cleanup = useCallback(() => {
    stopTimer();
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    mediaRecorderRef.current = null;
    chunksRef.current = [];
  }, [stopTimer]);

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  const startRecording = useCallback(async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Prefer webm for Whisper compatibility
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        stream.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
        stopTimer();
        if (blob.size > 0) {
          onRecordingComplete(blob);
        }
      };

      recorder.start(250); // collect in 250ms chunks
      setInternalState("recording");
      setDuration(0);

      timerRef.current = setInterval(() => {
        setDuration((d) => d + 1);
      }, 1000);
    } catch (err) {
      const msg =
        err instanceof DOMException && err.name === "NotAllowedError"
          ? "Microphone access denied. Please allow mic access."
          : "Could not access microphone.";
      setError(msg);
      cleanup();
    }
  }, [onRecordingComplete, cleanup, stopTimer]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    setInternalState("idle");
  }, []);

  const handleClick = useCallback(() => {
    if (state === "processing") return;
    if (state === "recording") {
      stopRecording();
    } else {
      startRecording();
    }
  }, [state, startRecording, stopRecording]);

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  const isLarge = size === "lg";

  return (
    <div className={cn("flex flex-col items-center gap-2", className)}>
      <button
        onClick={handleClick}
        disabled={state === "processing"}
        className={cn(
          "relative rounded-full flex items-center justify-center transition-all",
          isLarge ? "w-24 h-24" : "w-12 h-12",
          state === "idle" &&
            "bg-slate-800 text-white hover:bg-slate-700 active:scale-95",
          state === "recording" &&
            "bg-red-500 text-white hover:bg-red-600 active:scale-95",
          state === "processing" &&
            "bg-slate-300 text-slate-500 cursor-not-allowed"
        )}
      >
        {/* Pulsing ring while recording */}
        {state === "recording" && (
          <>
            <span className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-30" />
            <span className="absolute inset-[-4px] rounded-full border-2 border-red-300 animate-pulse" />
          </>
        )}

        {state === "processing" ? (
          <Loader2
            className={cn(
              "animate-spin",
              isLarge ? "w-10 h-10" : "w-5 h-5"
            )}
          />
        ) : state === "recording" ? (
          <MicOff className={cn(isLarge ? "w-10 h-10" : "w-5 h-5")} />
        ) : (
          <Mic className={cn(isLarge ? "w-10 h-10" : "w-5 h-5")} />
        )}
      </button>

      {/* Label */}
      <span
        className={cn(
          "text-center",
          isLarge ? "text-sm" : "text-[10px]",
          state === "recording"
            ? "text-red-600 font-medium"
            : "text-muted-foreground"
        )}
      >
        {state === "processing"
          ? "Processing..."
          : state === "recording"
          ? formatDuration(duration)
          : "Tap to speak"}
      </span>

      {/* Error */}
      {error && (
        <p className="text-xs text-red-600 text-center max-w-[200px]">
          {error}
        </p>
      )}
    </div>
  );
}
