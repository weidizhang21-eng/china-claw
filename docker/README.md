# 启动

docker-compose up -d

# 查看日志（调试 SQL 必备）

docker-compose logs -f postgres

# 连接数据库

psql -h localhost -U developer -d app_database

# 停止并保留数据

docker-compose down

# 完全重置（清除数据）

docker-compose down -v
