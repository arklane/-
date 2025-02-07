#!/bin/bash

echo "开始初始化数据库..."

# 使用root用户执行SQL文件
if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    read -sp "请输入MySQL root密码: " MYSQL_ROOT_PASSWORD
    echo
fi

# 使用环境变量或输入的密码执行SQL文件
mysql -u root -p"$MYSQL_ROOT_PASSWORD" < init_db.sql

# 验证用户创建和授权
mysql -u root -p"$MYSQL_ROOT_PASSWORD" << EOF
SELECT User, Host FROM mysql.user WHERE User = 'finance_user';
SHOW GRANTS FOR 'finance_user'@'localhost';
EOF

echo "数据库初始化完成"

# 测试finance_user连接
echo "测试finance_user连接..."
mysql -u finance_user -p123456 finance_data -e "SELECT 1;" && echo "连接测试成功!" || echo "连接测试失败!"
