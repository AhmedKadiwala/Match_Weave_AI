/** Deployment configuration. A public frontend never guesses a visitor's localhost API. */
const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]"]);
const configured = (import.meta.env.VITE_API_URL || "").trim();
const localPage = LOCAL_HOSTS.has(window.location.hostname);

function configuration() {
  if (configured) {
    try {
      const url = new URL(configured);
      if (
        !["https:", "http:"].includes(url.protocol) ||
        url.username ||
        url.password ||
        url.search ||
        url.hash ||
        !["", "/"].includes(url.pathname) ||
        /YOUR-|CHANGE-ME/i.test(configured)
      )
        throw Error();
      if (!LOCAL_HOSTS.has(url.hostname) && url.protocol !== "https:")
        throw Error();
      return {
        baseURL: url.origin,
        remote: !LOCAL_HOSTS.has(url.hostname),
        autoConnect: true,
        error: "",
      };
    } catch {
      return {
        baseURL: "",
        remote: false,
        autoConnect: false,
        error:
          "VITE_API_URL must be your actual HTTPS Render origin, without /api. Update it in Vercel and redeploy.",
      };
    }
  }
  if (localPage) {
    const sameOrigin = window.location.port === "8000";
    return {
      baseURL: sameOrigin ? window.location.origin : "http://127.0.0.1:8000",
      remote: false,
      autoConnect: sameOrigin,
      error: "",
    };
  }
  return {
    baseURL: "",
    remote: false,
    autoConnect: false,
    error:
      "This is recorded replay. Set VITE_API_URL to your Render backend in Vercel and redeploy to enable fresh workflows.",
  };
}

export const API_CONFIG = configuration();
