from typing import TypeVar

from app.services.redis import get_redis
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _get_model_name(model: type[BaseModel]) -> str:
    """Get the model name for Redis key prefixing."""
    return model.__name__


def _make_key(model_name: str, id: str) -> str:
    """Create Redis key with model name prefix."""
    return f"{model_name}:{id}"


async def save_data(id: str, data: T) -> None:
    """Save a Pydantic model instance to Redis."""
    redis = get_redis()
    model_name = _get_model_name(type(data))
    key = _make_key(model_name, id)

    # Serialize to JSON using Pydantic's built-in serialization
    json_data = data.model_dump_json()
    await redis.set(key, json_data)


async def get_data(id: str, model: type[T]) -> T:
    """Retrieve a Pydantic model instance from Redis."""
    redis = get_redis()
    model_name = _get_model_name(model)
    key = _make_key(model_name, id)

    json_data = await redis.get(key)
    if json_data is None:
        raise KeyError(f"No data found for {model_name} with id: {id}")

    # Ensure we have a string for JSON parsing
    if isinstance(json_data, bytes):
        json_data = json_data.decode("utf-8")

    # Deserialize from JSON using Pydantic's built-in deserialization
    return model.model_validate_json(json_data)


async def list_ids(model_name: str) -> list[str]:
    """List all IDs for a given model type."""
    redis = get_redis()
    pattern = f"{model_name}:*"

    # Get all keys matching the pattern
    keys = await redis.keys(pattern)

    # Extract IDs by removing the model name prefix
    ids = []
    prefix_len = len(model_name) + 1  # +1 for the colon
    for key in keys:
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        ids.append(key[prefix_len:])

    return ids


async def list_data(model: type[T]) -> list[T]:
    """List all instances of a given model type from Redis."""
    model_name = _get_model_name(model)
    ids = await list_ids(model_name)

    data_list = []
    for id in ids:
        try:
            data = await get_data(id, model)
            data_list.append(data)
        except KeyError:
            # Skip if data was deleted between listing and retrieval
            continue

    return data_list


async def delete_data(id: str, model: type[BaseModel]) -> bool:
    """Delete a model instance from Redis. Returns True if deleted, False if not found."""
    redis = get_redis()
    model_name = _get_model_name(model)
    key = _make_key(model_name, id)

    result = await redis.delete(key)
    return bool(result)


async def exists_data(id: str, model: type[BaseModel]) -> bool:
    """Check if a model instance exists in Redis."""
    redis = get_redis()
    model_name = _get_model_name(model)
    key = _make_key(model_name, id)

    result = await redis.exists(key)
    return bool(result)
