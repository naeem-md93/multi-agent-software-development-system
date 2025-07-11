# Modify Docker Compose to include scaling parameters
#!/bin/bash
cp docker-compose.yml docker-compose.backup.yml
sed -i 's/\(^  app:\)/\1\n    deploy:\n      replicas: 3\n      resources:\n        limits:\n          cpus: "2.0"\n        memory: "1G"/' docker-compose.yml
