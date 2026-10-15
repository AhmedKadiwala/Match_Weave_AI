"""Explicit local/Render configuration. Cloud deployments never invoke a PC-local model."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlparse

LOCAL_HOSTS = ("127.0.0.1", "localhost", "testserver", "[::1]")
LOCAL_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:4173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
)


@dataclass(frozen=True)
class Settings:
    deployment: str
    allowed_hosts: tuple[str, ...]
    cors_origins: tuple[str, ...]
    local_inference_enabled: bool

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None):
        env = os.environ if environ is None else environ
        deployment = env.get("MATCHWEAVE_DEPLOYMENT", "render" if env.get("RENDER") else "local")
        if deployment not in ("local", "render"):
            raise ValueError("MATCHWEAVE_DEPLOYMENT must be local or render")
        hosts = list(LOCAL_HOSTS)
        for host in [
            env.get("RENDER_EXTERNAL_HOSTNAME", ""),
            *env.get("MATCHWEAVE_ALLOWED_HOSTS", "").split(","),
        ]:
            host = host.strip().lower()
            if not host:
                continue
            if any(c in host for c in "/:@ ") or "*" in host:
                raise ValueError("Allowed hosts must be exact hostnames without scheme, path or wildcard")
            hosts.append(host)
        origins = list(LOCAL_ORIGINS)
        for origin in env.get("MATCHWEAVE_CORS_ORIGINS", "").split(","):
            origin = origin.strip().rstrip("/")
            if not origin:
                continue
            parsed = urlparse(origin)
            if (
                parsed.scheme not in ("http", "https")
                or not parsed.hostname
                or parsed.path
                or parsed.query
                or parsed.fragment
                or parsed.username
                or "*" in origin
            ):
                raise ValueError(
                    "CORS origins must be exact http(s) origins, e.g. https://your-app.vercel.app"
                )
            if deployment == "render" and parsed.scheme != "https":
                raise ValueError("Additional Render frontend origins must use HTTPS")
            origins.append(origin)
        return cls(
            deployment, tuple(dict.fromkeys(hosts)), tuple(dict.fromkeys(origins)), deployment == "local"
        )
