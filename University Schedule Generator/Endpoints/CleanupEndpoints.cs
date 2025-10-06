using Microsoft.AspNetCore.Mvc;
using University_Schedule_Generator.Services;

namespace University_Schedule_Generator.Endpoints;

public static class CleanupEndpoints
{
    public static IEndpointRouteBuilder MapCleanupEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapDelete("/cleanup", CleanupAllData)
            .WithName("CleanupAllData")
            .WithTags("Cleanup")
            .Produces<CleanupResult>(200)
            .Produces(500);

        return app;
    }

    private static async Task<IResult> CleanupAllData(
        [FromServices] DataCleanupService cleanupService)
    {
        try
        {
            var result = await cleanupService.CleanupAllDataAsync();
            
            if (result.Success)
            {
                return Results.Ok(result);
            }
            
            return Results.Problem(
                title: "Error during cleanup",
                detail: result.Message,
                statusCode: 500
            );
        }
        catch (Exception ex)
        {
            return Results.Problem(
                title: "Error during cleanup",
                detail: ex.Message,
                statusCode: 500
            );
        }
    }
}
