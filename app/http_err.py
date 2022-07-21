import fastapi


def http_err_decorator(func):
    def http_err(conditions=True, detail="Backender debil"):
        if conditions:
            func(detail=detail)
    return http_err

@http_err_decorator
def locked(conditions=True, detail="Locked"):
    raise fastapi.HTTPException(status_code=423, detail=detail)

@http_err_decorator
def bad_request(conditions=True, detail="Bad Request"):
    raise fastapi.HTTPException(status_code=400, detail=detail)

@http_err_decorator
def not_acceptable(conditions=True, detail="Not Acceptable"):
    raise fastapi.HTTPException(status_code=406, detail=detail)

@http_err_decorator
def unauthorized(conditions=True, detail="Unauthorizede"):
    raise fastapi.HTTPException(status_code=401, detail=detail)

@http_err_decorator
def not_found(conditions=True, detail="Not Found"):
    raise fastapi.HTTPException(status_code=404, detail=detail)

@http_err_decorator
def forbidden(conditions=True, detail="Forbidden"):
    raise fastapi.HTTPException(status_code=403, detail=detail)