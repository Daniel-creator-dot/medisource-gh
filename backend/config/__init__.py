__all__ = ("celery_app",)


def __getattr__(name):
    if name == "celery_app":
        from .celery import app as celery_app

        return celery_app
    raise AttributeError(name)
