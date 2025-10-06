using Elastic.Clients.Elasticsearch;
using Elastic.Clients.Elasticsearch.QueryDsl;
using Microsoft.AspNetCore.Mvc;

namespace University_Schedule_Generator.Endpoints;

public static class ElasticSearchEndpoints
{
    public static RouteGroupBuilder MapElasticSearchEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup(""); // Опциональный под-префикс
        
        // Получение всех материалов
        app.MapGet("/elastic_test", async ([FromServices] ElasticsearchClient esClient) =>
        {
            try
            {
                var response = await esClient.SearchAsync<dynamic>(s => s
                    .Index("materials")
                    .Size(100) // Ограничение на количество результатов
                );

                if (!response.IsValidResponse)
                {
                    return Results.Ok(new
                    {
                        total = 0,
                        documents = Array.Empty<object>(),
                        message = "Index 'materials' not found or empty. Please generate data first.",
                        error = response.DebugInformation
                    });
                }

                var documents = response.Documents?.ToList() ?? new List<dynamic>();
                
                return Results.Ok(new
                {
                    total = response.Total,
                    count = documents.Count,
                    documents = documents
                });
            }
            catch (Exception ex)
            {
                return Results.Ok(new
                {
                    total = 0,
                    documents = Array.Empty<object>(),
                    message = "Error accessing Elasticsearch. Index may not exist yet.",
                    error = ex.Message
                });
            }
        })
        .WithName("GetAllElasticData")
        .WithTags("Elastic");

        // Поиск по тексту лекции
        app.MapGet("/elastic_search", async ([FromServices] ElasticsearchClient esClient, string? q) =>
        {
            if (string.IsNullOrEmpty(q))
            {
                return Results.BadRequest("Query parameter 'q' is required");
            }

            try
            {
                var response = await esClient.SearchAsync<dynamic>(s => s
                    .Index("materials")
                    .Query(query => query
                        .MultiMatch(m => m
                            .Query(q)
                            .Fields(new[] { "name^2", "lecture_text" })
                        )
                    )
                    .Size(50)
                );

                if (!response.IsValidResponse)
                {
                    return Results.Ok(new
                    {
                        query = q,
                        total = 0,
                        documents = Array.Empty<object>(),
                        message = "Index 'materials' not found or empty.",
                        error = response.DebugInformation
                    });
                }

                var documents = response.Documents?.ToList() ?? new List<dynamic>();

                return Results.Ok(new
                {
                    query = q,
                    total = response.Total,
                    count = documents.Count,
                    documents = documents
                });
            }
            catch (Exception ex)
            {
                return Results.Ok(new
                {
                    query = q,
                    total = 0,
                    documents = Array.Empty<object>(),
                    message = "Error searching Elasticsearch.",
                    error = ex.Message
                });
            }
        })
        .WithName("SearchElasticData")
        .WithTags("Elastic");
        
        return group;
    }
}