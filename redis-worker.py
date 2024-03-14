import aioredis
import json


async def add_responses_to_redis():
    # Connect to Redis
    redis = aioredis.from_url("redis://localhost")
    try:
        # Define your data (message content or keywords as keys, responses as values)
        with open('./resources/messages-data.json') as f:
            data = json.load(f)

        # Add data to Redis
        for key, value in data.items():
            await redis.set(key.lower(), value)  # Convert key to lowercase for case-insensitive matching

        print("Data added to Redis successfully")
    except (aioredis.RedisError, OSError, json.decoder.JSONDecodeError) as e:
        print(f"An error occurred while adding data to redis database: {e}")
    finally:
        await redis.close()

# if __name__ == "__main__":
#     asyncio.run(add_responses_to_redis())