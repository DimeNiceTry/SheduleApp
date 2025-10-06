using Elastic.Clients.Elasticsearch;
using University_Schedule_Generator.Infrastructure.Generators.Data;
using University_Schedule_Generator.Interfaces.DataSaver;

namespace University_Schedule_Generator.Services.DataSavers;

public class ElasticDataSaver : IDataSaver<GeneratedData>
{
    private readonly ElasticsearchClient _esClient;
    private readonly ILogger<ElasticDataSaver> _logger;

    private class MaterialElasticDoc
    {
        /* ... как раньше ... */
        public int id { get; set; }
        public int id_lect { get; set; }
        public string name { get; set; }
        public string lecture_text { get; set; }
    }

    public ElasticDataSaver(ElasticsearchClient esClient, ILogger<ElasticDataSaver> logger)
    {
        _esClient = esClient;
        _logger = logger;
    }

    public async Task<SaveResult> SaveAsync(GeneratedData data)
    {
        _logger.LogInformation("Saving materials to Elasticsearch...");
        
        // Создаём индекс с правильным mapping, если он не существует
        await EnsureIndexExistsAsync();
        
        if (data.MaterialElastics.Any())
        {
            var elasticDocs = data.MaterialElastics.Select(m => new MaterialElasticDoc
            {
                id = m.Id,
                id_lect = m.LectureId,
                name = m.Name,
                lecture_text = m.Content
            });

            var bulkResponse = await _esClient.BulkAsync(b => b
                .Index("materials") // Имя индекса
                .IndexMany(elasticDocs)
            );

            if (!bulkResponse.IsValidResponse)
            {
                _logger.LogError("Error saving to Elasticsearch: {ErrorReason}", bulkResponse.DebugInformation);
            }
            else
            {
                _logger.LogInformation("Elasticsearch save complete. Indexed {Count} documents.", elasticDocs.Count());
            }
        }
        else
        {
            _logger.LogWarning("No MaterialElastic objects to save to Elasticsearch.");
        }
        return new SaveResult(true, "Elasticsearch save complete.");
    }

    private async Task EnsureIndexExistsAsync()
    {
        var indexName = "materials";
        var existsResponse = await _esClient.Indices.ExistsAsync(indexName);
        
        if (!existsResponse.Exists)
        {
            _logger.LogInformation("Creating Elasticsearch index '{IndexName}'...", indexName);
            
            var createResponse = await _esClient.Indices.CreateAsync(indexName, c => c
                .Mappings(m => m
                    .Properties<MaterialElasticDoc>(p => p
                        .IntegerNumber(n => n.id)
                        .IntegerNumber(n => n.id_lect)
                        .Text(t => t.name, t => t.Analyzer("russian"))
                        .Text(t => t.lecture_text, t => t.Analyzer("russian"))
                    )
                )
                .Settings(s => s
                    .Analysis(a => a
                        .Analyzers(an => an
                            .Custom("russian", ca => ca
                                .Tokenizer("standard")
                                .Filter(new[] { "lowercase", "russian_stop", "russian_stemmer" })
                            )
                        )
                        .TokenFilters(tf => tf
                            .Stop("russian_stop", st => st.Stopwords(new[] { "_russian_" }))
                            .Stemmer("russian_stemmer", st => st.Language("russian"))
                        )
                    )
                )
            );
            
            if (createResponse.IsValidResponse)
            {
                _logger.LogInformation("Index '{IndexName}' created successfully.", indexName);
            }
            else
            {
                _logger.LogError("Failed to create index '{IndexName}': {Error}", indexName, createResponse.DebugInformation);
            }
        }
    }
}