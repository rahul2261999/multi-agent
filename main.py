import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()


def _str_to_bool(value: str) -> bool:
    value_lower = value.strip().lower()
    return value_lower in {"1", "true", "yes", "on"}


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = _str_to_bool(os.getenv("RELOAD", "false"))

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload_enabled,
    )


if __name__ == "__main__":
    main()
