curl -X POST --user roy:1234 -H "Content-Type:application/json" -d '{\"name\":\"batman\",\"alias\":\"asd2\"}' http://localhost:8000/api/heroes/


curl -X DELETE --user roy:1234  http://localhost:8000/api/models/10