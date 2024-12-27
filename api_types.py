from dataclasses import dataclass, asdict, field

@dataclass
class ErrorDetail:
    message: str = field(default="")
    type: str = field(default="")
    code: int = 0
    error_subcode: int = field(default=0)
    is_transient: bool = False
    error_user_title: str = field(default="")
    error_user_msg: str = field(default="")
    fbtrace_id: str = field(default="")

@dataclass
class Error:
    error: ErrorDetail

    def to_json(self):
        return asdict(self)

@dataclass
class TokenResponse:
    access_token: str
    token_type: str
    expires_in: str

    def to_json(self):
        return asdict(self)

@dataclass
class IDResponse:
    id: str

    def to_json(self):
        return asdict(self)