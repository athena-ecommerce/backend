import redis

from CORE import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB

# Cliente único de conexão com o Redis, reaproveitado em todas as requisições.
# decode_responses=True faz o redis já devolver str em vez de bytes.

redis_cliente = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
)


def pegar_redis() -> redis.Redis:
    return redis_cliente
