import docker
import logging

logger = logging.getLogger(__name__)

_client = None

def get_docker_client():
    global _client
    if _client is None:
        try:
            _client = docker.from_env()
            _client.version()
            return _client
        except Exception as e:
            logger.error(f"CRITICAL: Docker Engine is unreachable. Error: {e}")
            raise RuntimeError("Docker Engine is unreachable") from e
    return _client
