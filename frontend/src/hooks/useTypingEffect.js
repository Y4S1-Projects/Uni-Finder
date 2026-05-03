import { useEffect, useRef, useState } from "react";

export function useTypingEffect(text, speed = 20, shouldStart = true) {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [hasCompleted, setHasCompleted] = useState(false);
  const intervalRef = useRef(null);
  const previousTextRef = useRef(text);

  useEffect(() => {
    if (previousTextRef.current !== text) {
      previousTextRef.current = text;
      setDisplayedText("");
      setIsTyping(false);
      setHasCompleted(false);
    }
  }, [text]);

  useEffect(() => {
    if (!text || !shouldStart || hasCompleted) return undefined;

    setIsTyping(true);
    let currentIndex = 0;
    const step = Math.max(1, Math.floor(speed / 10));
    const intervalMs = Math.max(12, speed);

    intervalRef.current = setInterval(() => {
      currentIndex += step;
      if (currentIndex >= text.length) {
        setDisplayedText(text);
        setIsTyping(false);
        setHasCompleted(true);
        if (intervalRef.current) clearInterval(intervalRef.current);
        return;
      }
      setDisplayedText(text.slice(0, currentIndex));
    }, intervalMs);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [hasCompleted, shouldStart, speed, text]);

  return { displayedText, isTyping, hasCompleted };
}
