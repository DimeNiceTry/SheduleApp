using System.Text;
using Bogus;
using Elastic.Clients.Elasticsearch;
using Microsoft.EntityFrameworkCore;
using MongoDB.Driver;
using Neo4j.Driver;
using StackExchange.Redis;
using University_Schedule_Generator.Infrastructure.Generators.Data;
using University_Schedule_Generator.Services.Generators;

namespace University_Schedule_Generator.Services;

public class GeneratorService
{
    private readonly Faker _faker;
    
    private readonly ILogger<GeneratorService> _logger;

    public GeneratorService(
        ILogger<GeneratorService> logger)
    {
        _logger = logger;
        _faker = new Faker("ru");
    }

    public GeneratedData GenerateForPostgres(int SpecialtiesCount=300, int UniversityCount=3,
        int InstitutionCount=30, int DepartmentCount=300
    , int groupCount=100, int StudentCount=1000, int CourseCount=100)
    {
        _logger.LogInformation("Starting data generation (in memory)...");

        var specialityGenerator = new SpecialtyGenerator(_faker);
        // --- Генерация данных (без сохранения) ---
        _logger.LogDebug("Generating Specialties...");
        var Specialties = new List<Speciality>();
        for (int i = 0; i < SpecialtiesCount; i++)
        {
            var speciality = specialityGenerator.GenerateSpecialty();
            Specialties.Add(speciality);
        }


        _logger.LogDebug("Generating Universities...");
        var universityGenerator = new UniversityNameGenerator(_faker);
        var Universities = new List<University>();
        for (int i = 0; i < UniversityCount; i++)
        {
            var university = universityGenerator.Generate();
            Universities.Add(new University() { Name = university });
        }

        _logger.LogDebug("Generating Institutes...");
        var instituteGenerator = new InstituteGenerator(_faker, Universities);
        var Institutes = new List<Institute>();
        for (int i = 0; i < InstitutionCount; i++)
        {
            var institute = instituteGenerator.GenerateInstituteData();
            Institutes.Add(institute);
        }

        _logger.LogDebug("Generating Departments...");
        //генерируем департаменты
        var departmentgenerator = new DepartmentGenerator(_faker, Institutes);
        var Departments = new List<Department>();
        for (int i = 0; i < DepartmentCount; i++)
        {
            var department = departmentgenerator.GenerateDepartmentData();
            Departments.Add(department);
        }

        _logger.LogDebug("Generating Groups...");
        //генерируем группы
        var groupGenerator = new GroupGenerator(_faker, Departments);
        var Groups = new List<Group>();
        for (int i = 0; i < groupCount; i++)
        {
            var group = groupGenerator.GenerateGroupData();
            Groups.Add(group);
        }

        _logger.LogDebug("Generating Students...");
        //генерим студентов
        var studentGenerator = new StudentGenerator(_faker, Groups);
        var Students = new List<Student>();
        for (int i = 0; i < StudentCount; i++)
        {
            var student = studentGenerator.GenerateStudentData();
            Students.Add(student);
        }

        _logger.LogDebug("Generating Courses...");
        var courcesGenerator = new CourseGenerator(_faker, Departments, Specialties);
        var courses = new List<Course>();
        for (int i = 0; i < CourseCount; i++)
        {
            var course = courcesGenerator.GenerateCourse();
            courses.Add(course);
        }

        _logger.LogDebug("Generating Lectures...");
        var lectureGenerator = new LectureGenerator(_faker);
        List<Lecture> Lectures = new List<Lecture>();
        foreach (var course in courses)
        {
            var lectureForCourse = lectureGenerator.GenerateLecturesForCourse(course);
            Lectures.AddRange(lectureForCourse);
        }

        _logger.LogDebug("Generating Materials...");
        var materialGenerator = new MaterialGenerator(_faker);
        var materials = new List<Material>();
        foreach (var lecture in Lectures)
        {
            var materialsForLecture = materialGenerator.GenerateMaterialsForLecture(lecture);
            materials.AddRange(materialsForLecture);
        }

        _logger.LogDebug("Generating Schedules...");
        var scheduleGenerator = new ScheduleGenerator(_faker);
        var schedules = scheduleGenerator.Generate(Groups, Lectures, Lectures.Count*10);

        _logger.LogDebug("Generating Visits...");
        var visitGenerator = new VisitGenerator(_faker);
        var allGeneratedVisits = new List<Visit>(); // Собираем сюда все корректные посещения
        foreach (var group in Groups) // Или итерируйте по уникальным GroupId
        {
            // 1. Отфильтровать студентов ТОЛЬКО этой группы
            var studentsInThisGroup = Students.Where(s => s.Group == group).ToList();

            // 2. Отфильтровать расписание ТОЛЬКО для этой группы
            var scheduleForThisGroup = schedules.Where(sch => sch.Group== group).ToList();

            // 3. Генерировать посещения ТОЛЬКО для этой группы и ЕЕ расписания
            if (studentsInThisGroup.Any() && scheduleForThisGroup.Any())
            {
                var visitsForThisGroup = visitGenerator.Generate(
                    studentsInThisGroup,
                    scheduleForThisGroup
                );
                allGeneratedVisits.AddRange(visitsForThisGroup);
            }
        }
        // Append a deterministic test bundle for Lab1 validation
        const string UNIQUE_TOKEN = "LAB1_UNIQUE_TOKEN_2025";
        try
        {
            var testDepartment = Departments.FirstOrDefault() ?? throw new InvalidOperationException("No departments generated");
            var testSpeciality = Specialties.FirstOrDefault() ?? throw new InvalidOperationException("No specialties generated");
            var testGroup = Groups.FirstOrDefault(g => (Students?.Any(s => s.Group == g) ?? false))
                             ?? Groups.FirstOrDefault() ?? throw new InvalidOperationException("No groups generated");

            var testCourse = new Course
            {
                Name = $"Special Course {UNIQUE_TOKEN}",
                Department = testDepartment,
                DepartmentId = testDepartment.Id,
                Speciality = testSpeciality,
                SpecialityId = testSpeciality.Id,
                Term = "2025-2026"
            };

            var testLecture = new Lecture
            {
                Name = $"Introduction to {UNIQUE_TOKEN}",
                Requirements = false,
                Course = testCourse,
                CourseId = testCourse.Id,
                Year = 2025,
                FullText = $"This is a deterministic lecture used for Lab1 checks. Marker: {UNIQUE_TOKEN}."
            };

            var testMaterial = new Material
            {
                Name = $"Reading Material {UNIQUE_TOKEN}",
                Lecture = testLecture,
                LectureId = testLecture.Id
            };

            var sStart = DateTime.UtcNow.Date.AddDays(3).AddHours(10);
            var testSchedule = new Schedule
            {
                Lecture = testLecture,
                LectureId = testLecture.Id,
                Group = testGroup,
                GroupId = testGroup.Id,
                StartTime = sStart,
                EndTime = sStart.AddHours(2)
            };

            var studentsOfGroup = Students.Where(s => s.Group == testGroup).Take(15).ToList();
            var attendedSubset = studentsOfGroup.Take(4).ToList();
            foreach (var stud in attendedSubset)
            {
                allGeneratedVisits.Add(new Visit
                {
                    Student = stud,
                    StudentId = stud.Id,
                    Schedule = testSchedule,
                    ScheduleId = testSchedule.Id,
                    VisitTime = testSchedule.StartTime.AddMinutes(15)
                });
            }

            courses.Add(testCourse);
            Lectures.Add(testLecture);
            materials.Add(testMaterial);
            schedules.Add(testSchedule);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to append deterministic Lab1 test data. Generation will proceed without it.");
        }

        var generatedData = new GeneratedData()
        {
            Visits = allGeneratedVisits,
            Institutes = Institutes,
            Departments = Departments,
            Groups = Groups,
            Students = Students,
            Lectures = Lectures,
            Materials = materials,
            Schedules = schedules,
            Courses = courses,
            Specialities = Specialties,
            Universities = Universities,
        };
        return generatedData;
    }

    public GeneratedData GenerateDataForElastic(GeneratedData generatedData)
    {
        var elasticGenerator = new MaterialElasticGenerator(_faker);
        generatedData.MaterialElastics = elasticGenerator.Generate(generatedData.Materials);
        return generatedData;
    }
}
