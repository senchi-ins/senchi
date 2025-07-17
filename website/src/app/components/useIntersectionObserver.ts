'use client';

import { useEffect, useRef, useState } from 'react';

interface UseIntersectionObserverOptions {
  threshold?: number;
  rootMargin?: string;
  triggerOnce?: boolean;
}

export function useIntersectionObserver(options: UseIntersectionObserverOptions = {}) {
  const { threshold = 0.1, rootMargin = '0px', triggerOnce = true } = options;
  const [isIntersecting, setIsIntersecting] = useState(false);
  const ref = useRef<HTMLElement>(null);
  const observer = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    observer.current = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsIntersecting(true);
        else setIsIntersecting(false);
      },
      { threshold: threshold ?? 0, root: null, rootMargin: rootMargin ?? '0px' }
    );

    observer.current.observe(element);

    return () => {
      observer.current?.unobserve(element);
    };
  }, [threshold, rootMargin, triggerOnce]);

  return { ref, isIntersecting };
} 