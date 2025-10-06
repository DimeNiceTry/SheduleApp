using University_Schedule_Generator.Contracts.Generator;
using University_Schedule_Generator.Services;

namespace University_Schedule_Generator.Endpoints;

public static class GeneratorEndpoints
{
    public static IEndpointRouteBuilder MapGeneratorEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapPost("generate", GenerateAndSaveData)
            .WithName("GenerateData")
            .WithTags("Generator")
            .WithDescription("Generate and save test data to all databases");

        return app;
    }

    public static async Task<IResult> GenerateAndSaveData(GenerateRequest request, DataSaverService dataSaverService)
    {
        try
        {
            await dataSaverService.GenerateAndSaveDataAsync(request.SpecialtiesCount,
                request.UniversityCount,
                request.InstitutionCount, 
                request.DepartmentCount, 
                request.GroupCount, 
                request.StudentCount,
                request.CourseCount);
            
            return Results.Ok(new 
            { 
                success = true,
                message = "Data generated and saved successfully to all databases"
            });
        }
        catch (Exception ex)
        {
            return Results.Problem(
                detail: ex.Message,
                statusCode: 500,
                title: "Error generating data"
            );
        }
    }

}