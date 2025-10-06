using Elastic.Clients.Elasticsearch;
using MongoDB.Driver;
using Neo4j.Driver;
using StackExchange.Redis;
using Microsoft.EntityFrameworkCore;
using University_Schedule_Generator;

namespace University_Schedule_Generator.Services;

public class DataCleanupService
{
    private readonly ApplicationContext _dbContext;
    private readonly ElasticsearchClient _esClient;
    private readonly IMongoDatabase _mongoDb;
    private readonly IDriver _neo4jDriver;
    private readonly IConnectionMultiplexer _redis;
    private readonly ILogger<DataCleanupService> _logger;

    public DataCleanupService(
        ApplicationContext dbContext,
        ElasticsearchClient esClient,
        IMongoDatabase mongoDb,
        IDriver neo4jDriver,
        IConnectionMultiplexer redis,
        ILogger<DataCleanupService> logger)
    {
        _dbContext = dbContext;
        _esClient = esClient;
        _mongoDb = mongoDb;
        _neo4jDriver = neo4jDriver;
        _redis = redis;
        _logger = logger;
    }

    public async Task<CleanupResult> CleanupAllDataAsync()
    {
        var result = new CleanupResult();

        try
        {
            // 1. Очистка PostgreSQL
            _logger.LogInformation("Cleaning PostgreSQL...");
            await CleanupPostgresAsync();
            result.PostgresCleared = true;
            _logger.LogInformation("PostgreSQL cleaned successfully");

            // 2. Очистка Redis
            _logger.LogInformation("Cleaning Redis...");
            await CleanupRedisAsync();
            result.RedisCleared = true;
            _logger.LogInformation("Redis cleaned successfully");

            // 3. Очистка MongoDB
            _logger.LogInformation("Cleaning MongoDB...");
            await CleanupMongoAsync();
            result.MongoCleared = true;
            _logger.LogInformation("MongoDB cleaned successfully");

            // 4. Очистка Neo4j
            _logger.LogInformation("Cleaning Neo4j...");
            await CleanupNeo4jAsync();
            result.Neo4jCleared = true;
            _logger.LogInformation("Neo4j cleaned successfully");

            // 5. Очистка Elasticsearch
            _logger.LogInformation("Cleaning Elasticsearch...");
            await CleanupElasticsearchAsync();
            result.ElasticsearchCleared = true;
            _logger.LogInformation("Elasticsearch cleaned successfully");

            result.Success = true;
            result.Message = "All data cleared successfully from all databases";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during cleanup");
            result.Success = false;
            result.Message = $"Error during cleanup: {ex.Message}";
        }

        return result;
    }

    private async Task CleanupPostgresAsync()
    {
        // Удаляем данные в правильном порядке (учитывая foreign keys)
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Visits\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Schedules\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Materials\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Lectures\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Students\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Courses\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Groups\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Departments\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Institutes\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Universities\"");
        await _dbContext.Database.ExecuteSqlRawAsync("DELETE FROM \"Specialities\"");

        // Сброс последовательностей (sequences) для автоинкремента
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Visits_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Schedules_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Materials_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Lectures_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Students_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Courses_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Groups_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Departments_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Institutes_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Universities_Id_seq\" RESTART WITH 1");
        await _dbContext.Database.ExecuteSqlRawAsync("ALTER SEQUENCE \"Specialities_Id_seq\" RESTART WITH 1");
    }

    private async Task CleanupRedisAsync()
    {
        var db = _redis.GetDatabase();
        var endpoints = _redis.GetEndPoints();
        
        foreach (var endpoint in endpoints)
        {
            var server = _redis.GetServer(endpoint);
            
            // Получаем все ключи с паттерном student:*
            var keys = server.Keys(pattern: "student:*").ToArray();
            
            if (keys.Length > 0)
            {
                // Удаляем все найденные ключи
                await db.KeyDeleteAsync(keys);
                _logger.LogInformation("Deleted {Count} keys from Redis", keys.Length);
            }
        }
    }

    private async Task CleanupMongoAsync()
    {
        // Получаем все коллекции
        var collections = await _mongoDb.ListCollectionNamesAsync();
        
        await collections.ForEachAsync(async collectionName =>
        {
            var collection = _mongoDb.GetCollection<MongoDB.Bson.BsonDocument>(collectionName);
            await collection.DeleteManyAsync(MongoDB.Bson.BsonDocument.Parse("{}"));
        });
    }

    private async Task CleanupNeo4jAsync()
    {
        await using var session = _neo4jDriver.AsyncSession();
        
        // Удаляем все узлы и связи
        await session.ExecuteWriteAsync(async tx =>
        {
            await tx.RunAsync("MATCH (n) DETACH DELETE n");
        });
    }

    private async Task CleanupElasticsearchAsync()
    {
        // Удаляем индекс materials, если существует
        var existsResponse = await _esClient.Indices.ExistsAsync("materials");
        
        if (existsResponse.Exists)
        {
            await _esClient.Indices.DeleteAsync("materials");
        }
    }
}

public class CleanupResult
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public bool PostgresCleared { get; set; }
    public bool RedisCleared { get; set; }
    public bool MongoCleared { get; set; }
    public bool Neo4jCleared { get; set; }
    public bool ElasticsearchCleared { get; set; }
}
