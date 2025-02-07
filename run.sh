#!/bin/bash

echo "基金管理系统初始化工具"

# 数据库初始化函数
init_database() {
    local root_pass="$1"
    echo "正在初始化数据库..."
    
    # 使用root用户创建数据库和用户
    mysql -u root -p"$root_pass" << EOF
CREATE DATABASE IF NOT EXISTS finance_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'finance_user'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON finance_data.* TO 'finance_user'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    if [ $? -eq 0 ]; then
        echo "数据库初始化成功"
        # 使用finance_user创建表结构
        MYSQL_PWD=123456 mysql -u finance_user finance_data < init_db.sql
        return 0
    else
        echo "数据库初始化失败"
        return 1
    fi
}

# 检查MySQL连接
check_mysql_connection() {
    echo "检查MySQL连接..."
    if ! mysql -u finance_user -p123456 -e "USE finance_data;" 2>/dev/null; then
        echo "无法连接到数据库，需要初始化"
        read -s -p "请输入MySQL root密码: " root_pass
        echo
        init_database "$root_pass"
        if [ $? -ne 0 ]; then
            echo "数据库初始化失败，请检查root密码是否正确"
            exit 1
        fi
    fi
}

# 主程序
echo "开始系统初始化..."
check_mysql_connection

# 确保data目录存在
mkdir -p data

# 导入数据
echo "导入基金数据..."
python3 import_csv.py

# 启动应用
echo "启动应用..."
python3 run.py
