import logging

try:
    import structlog  # type: ignore
except ImportError:  # Fallback ligero si no está instalado
    class _StructlogShim:
        def get_logger(self, name):
            return logging.getLogger(name)

        class contextvars:
            @staticmethod
            def bind_contextvars(**kwargs):
                pass

            @staticmethod
            def clear_contextvars():
                pass

    structlog = _StructlogShim()  # type: ignore


def configure_logging():
    level = logging.INFO
    try:
        logging.basicConfig(level=level, format='%(asctime)s %(name)s %(levelname)s %(message)s')
        if hasattr(structlog, 'configure'):
            processors = []
            try:
                processors = [
                    getattr(structlog, 'contextvars', type('cv', (), {'merge_contextvars': lambda **_: None})).merge_contextvars,
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                ]
                # Renderizador
                processors.append(getattr(structlog.processors, 'JSONRenderer', structlog.dev.ConsoleRenderer)())
            except Exception:
                processors = []
            try:
                structlog.configure(
                    processors=processors,
                    context_class=dict,
                    logger_factory=getattr(structlog, 'PrintLoggerFactory', lambda: None)(),
                    cache_logger_on_first_use=True,
                )
            except Exception:
                pass
    except Exception:
        logging.basicConfig(level=level)
