class ServiceError(Exception):
    """Base class for domain/service errors."""
    status_code: int = 400


class NotFoundError(ServiceError):
    status_code = 404


class ConflictError(ServiceError):
    status_code = 409


class ForbiddenError(ServiceError):
    status_code = 403


class AuthError(ServiceError):
    status_code = 401
