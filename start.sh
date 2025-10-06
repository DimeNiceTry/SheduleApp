#!/bin/bash

# Скрипт для быстрого запуска и проверки Schedule App

echo "🚀 Starting Schedule App..."
echo ""

# Запуск всех сервисов
echo "📦 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

# Проверка статуса
echo ""
echo "✅ Checking services status..."
docker-compose ps

echo ""
echo "🌐 Available Services:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 API Services:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  C# Generator:      http://localhost:8000"
echo "  Python Lab1:       http://localhost:8100"
echo "  Python Gateway:    http://localhost:8200"
echo "  Swagger Docs:      http://localhost:8200/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 Database UI Tools:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Kibana:            http://localhost:5601"
echo "  pgAdmin:           http://localhost:5050"
echo "    └─ Login:        admin@admin.com / admin"
echo "  Mongo Express:     http://localhost:8081"
echo "    └─ Login:        admin / admin"
echo "  Redis Commander:   http://localhost:8082"
echo "  Neo4j Browser:     http://localhost:7474"
echo "    └─ Login:        neo4j / password"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗄️ Direct Database Access:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PostgreSQL:        localhost:5432"
echo "  Redis:             localhost:6379"
echo "  MongoDB:           localhost:27017"
echo "  Neo4j (Bolt):      localhost:7687"
echo "  Elasticsearch:     localhost:9200"
echo ""

# Проверка доступности Elasticsearch
echo "🔍 Testing Elasticsearch..."
curl -s http://localhost:9200/_cluster/health?pretty > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Elasticsearch is ready"
else
    echo "  ⚠️  Elasticsearch is starting... (may take a few more seconds)"
fi

# Проверка доступности PostgreSQL
echo "🔍 Testing PostgreSQL..."
docker exec postgres pg_isready -U postgres > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ PostgreSQL is ready"
else
    echo "  ⚠️  PostgreSQL is starting..."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Generate test data:"
echo "   curl -X POST http://localhost:8000/generate \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"specialtiesCount\":5,\"universityCount\":2,\"institutionCount\":3,\"departmentCount\":5,\"groupCount\":10,\"studentCount\":100,\"courseCount\":20}'"
echo ""
echo "2. Check Elasticsearch data:"
echo "   curl http://localhost:8000/elastic_test"
echo ""
echo "3. Open UI tools in your browser (links above)"
echo ""
echo "4. View logs:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "5. Stop all services:"
echo "   docker-compose down"
echo ""
echo "6. Stop and remove all data:"
echo "   docker-compose down -v"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 For detailed instructions, see:"
echo "   - README.md"
echo "   - UI_TOOLS_GUIDE.md"
echo ""
echo "✨ Schedule App is ready!"
