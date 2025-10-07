import os
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
import psycopg
from neo4j import AsyncGraphDatabase


class DatabaseConnections:
    """Класс для управления подключениями ко всем БД"""
    
    def __init__(self):
        self.mongo_client: AsyncIOMotorClient = None
        self.redis_client: Redis = None
        self.postgres_conn = None
        self.neo4j_driver = None
    
    async def connect(self):
        """Подключиться ко всем базам данных"""
        # MongoDB
        mongo_uri = os.getenv("LAB3_MONGO_URI", "mongodb://mongo:27017")
        self.mongo_client = AsyncIOMotorClient(mongo_uri)
        
        # Redis
        redis_host = os.getenv("LAB3_REDIS_HOST", "redis")
        redis_port = int(os.getenv("LAB3_REDIS_PORT", "6379"))
        self.redis_client = Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # PostgreSQL
        postgres_dsn = os.getenv(
            "LAB3_POSTGRES_DSN",
            "postgresql://postgres:postgres@postgres:5432/university"
        )
        self.postgres_conn = await psycopg.AsyncConnection.connect(postgres_dsn)
        
        # Neo4j
        neo4j_uri = os.getenv("LAB3_NEO4J_URI", "bolt://neo4j:7687")
        neo4j_user = os.getenv("LAB3_NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("LAB3_NEO4J_PASSWORD", "password")
        self.neo4j_driver = AsyncGraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
    
    async def close(self):
        """Закрыть все подключения"""
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        if self.postgres_conn:
            await self.postgres_conn.close()
        
        if self.neo4j_driver:
            await self.neo4j_driver.close()
    
    def get_mongo_db(self):
        """Получить MongoDB database"""
        db_name = os.getenv("LAB3_MONGO_DB", "university")
        return self.mongo_client[db_name]
