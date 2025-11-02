const listeners = new Set();

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function toast(message, type = "info") {
  listeners.forEach((fn) => fn({ id: Date.now() + Math.random(), message, type }));
}

toast.success = (m) => toast(m, "success");
toast.error = (m) => toast(m, "error");

export default toast;

