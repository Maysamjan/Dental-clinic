"use client";
import { useEffect, useRef } from "react";
import { WS_URL } from "@/lib/api";
import { useAuth } from "@/stores/auth";

/**
 * Subscribe to a backend WebSocket channel (e.g. "workflow" or "dashboard").
 * Calls `onMessage` with each parsed { event, payload } frame.
 */
export function useWebSocket(
  path: string,
  onMessage: (msg: { event: string; payload: any }) => void
) {
  const access = useAuth((s) => s.access);
  const handlerRef = useRef(onMessage);
  handlerRef.current = onMessage;

  useEffect(() => {
    if (!access) return;
    const url = `${WS_URL}/${path}/?token=${access}`;
    let socket: WebSocket | null = null;
    let closedByUs = false;

    try {
      socket = new WebSocket(url);
      socket.onmessage = (e) => {
        try {
          handlerRef.current(JSON.parse(e.data));
        } catch {
          /* ignore malformed frames */
        }
      };
    } catch {
      /* WebSocket unavailable */
    }

    return () => {
      closedByUs = true;
      socket?.close();
    };
  }, [access, path]);
}
