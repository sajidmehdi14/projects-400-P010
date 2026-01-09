#!/bin/bash

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "Task API CRUD Tests"
echo "=========================================="

echo -e "\n1. POST /tasks - Create Task 1"
curl -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "completed": false
  }'

echo -e "\n\n2. POST /tasks - Create Task 2"
curl -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Setup CI/CD pipeline",
    "description": "Configure GitHub Actions",
    "completed": false
  }'

echo -e "\n\n3. POST /tasks - Create Task 3"
curl -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write unit tests",
    "description": "Add pytest coverage",
    "completed": true
  }'

echo -e "\n\n4. GET /tasks - Get All Tasks"
curl -X GET "$BASE_URL/tasks"

echo -e "\n\n5. GET /tasks/1 - Get Task by ID"
curl -X GET "$BASE_URL/tasks/1"

echo -e "\n\n6. PUT /tasks/1 - Update Task"
curl -X PUT "$BASE_URL/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation - UPDATED",
    "description": "Write comprehensive API documentation with examples",
    "completed": true
  }'

echo -e "\n\n7. PUT /tasks/2 - Partial Update (only completed)"
curl -X PUT "$BASE_URL/tasks/2" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'

echo -e "\n\n8. GET /tasks - Get All Tasks After Updates"
curl -X GET "$BASE_URL/tasks"

echo -e "\n\n9. DELETE /tasks/3 - Delete Task"
curl -X DELETE "$BASE_URL/tasks/3"

echo -e "\n\n10. GET /tasks - Get All Tasks After Delete"
curl -X GET "$BASE_URL/tasks"

echo -e "\n\n11. GET /tasks/3 - Try to Get Deleted Task (should return 404)"
curl -X GET "$BASE_URL/tasks/3"

echo -e "\n\n12. GET /tasks/999 - Try to Get Non-Existent Task (should return 404)"
curl -X GET "$BASE_URL/tasks/999"

echo -e "\n\n=========================================="
echo "CRUD Tests Completed"
echo "=========================================="
