from pydantic import BaseModel, Field, SecretStr, field_validator

class RedisConfig(BaseModel):
    host: str = 'localhost'
    port: int = 6379
    username: str = 'default'
    password: SecretStr 
    db: int = 0
    ssl: bool = True
    connection_timeout: int = 10
    
    @field_validator('port', 'db', 'connection_timeout', mode='before')
    @classmethod
    def convert_string_to_int(cls, v):
        if isinstance(v, str):
            return int(v)
        return v
    
    @field_validator('ssl', mode='before')
    @classmethod
    def convert_string_to_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v