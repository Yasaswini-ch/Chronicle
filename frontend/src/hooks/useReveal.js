import { useEffect, useRef, useState } from 'react';

// Fires once, the first time the element scrolls into view, then stays true.
export default function useReveal(options) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return undefined;
    if (typeof IntersectionObserver === 'undefined') {
      setVisible(true);
      return undefined;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.unobserve(node);
          }
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px', ...options }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return [ref, visible];
}
