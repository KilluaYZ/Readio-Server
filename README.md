# ReadIO 后端服务

ReadIO 项目的后端服务，基于 Flask 框架开发，为 Android App 和后台管理系统提供统一的 RESTful API 服务。

## 📋 项目简介

ReadIO 后端服务采用 Flask 框架，提供完整的用户认证、内容管理、文件处理等功能。系统采用模块化设计，支持多格式电子书处理，使用 MySQL 数据库存储数据，可选 Redis 缓存提升性能。

### 主要功能

- 🔐 **用户认证**：App 和 Web 端用户登录注册、Token 管理
- 📚 **书籍管理**：书籍信息管理、多格式支持（EPUB、TXT、MOBI、PDF）
- 💬 **社区功能**：帖子管理、评论系统、标签系统
- ✍️ **作品管理**：二创作品上传、审核、管理
- 📁 **文件管理**：电子书文件上传、存储、下载
- 📊 **数据统计**：阅读统计、用户行为分析
- 🔍 **系统监控**：服务器监控、日志管理

## 🛠️ 技术栈

### 核心技术

- **Web 框架**：Flask
- **数据库**：MySQL 5.7+
- **缓存**：Redis（可选）
- **ORM**：SQLAlchemy
- **任务调度**：APScheduler
- **跨域支持**：Flask-CORS

### 主要依赖

```txt
flask                  # Web 框架
PyMySql                # MySQL 驱动
flask_cors             # 跨域支持
sqlalchemy             # ORM 框架
DButils                # 数据库连接池
psutil                 # 系统监控
flask_apscheduler      # 定时任务
bs4                    # HTML 解析
pdfminer               # PDF 解析
mobi                   # MOBI 格式支持
ebooklib               # EPUB 格式支持
chardet                # 字符编码检测
```

## 📁 项目结构

```
Readio-Server/
├── readio/                      # 核心模块
│   ├── __init__.py              # Flask App 工厂函数
│   │
│   ├── auth/                     # 认证授权模块
│   │   ├── __init__.py
│   │   ├── appAuth.py            # App 端认证（登录、注册、Token）
│   │   ├── webAuth.py            # Web 端认证（后台管理系统）
│   │   └── routerdata.py         # 路由数据（菜单权限）
│   │
│   ├── database/                 # 数据库模块
│   │   ├── __init__.py
│   │   ├── connectPool.py       # 数据库连接池
│   │   ├── init_db.py            # 数据库初始化
│   │   ├── init.sql              # 数据库表结构
│   │   └── data1.txt             # 初始化数据
│   │
│   ├── mainpage/                 # 主页相关
│   │   ├── __init__.py
│   │   ├── appHomePage.py        # 首页推荐（好句、好书）
│   │   ├── appBookShelfPage.py   # 书架管理
│   │   ├── appBookDetailsPage.py # 书籍详情
│   │   ├── appBookReadPage.py    # 阅读页面
│   │   └── visualization.py       # 数据可视化
│   │
│   ├── manage/                   # 管理功能模块
│   │   ├── __init__.py
│   │   ├── userManage.py         # 用户管理
│   │   ├── postManage.py         # 帖子管理
│   │   ├── tagManage.py          # 标签管理
│   │   ├── worksManage.py        # 作品管理
│   │   └── fileManage.py         # 文件管理
│   │
│   ├── monitor/                   # 监控模块
│   │   ├── __init__.py
│   │   └── monitor.py             # 服务器监控
│   │
│   ├── utils/                     # 工具模块
│   │   ├── __init__.py
│   │   ├── auth.py                # 认证工具
│   │   ├── buildResponse.py       # 响应构建
│   │   ├── check.py                # 数据校验
│   │   ├── executeSQL.py           # SQL 执行
│   │   ├── filechange.py          # 文件转换
│   │   ├── formatter.py           # 数据格式化
│   │   ├── json.py                # JSON 处理
│   │   └── myExceptions.py        # 自定义异常
│   │
│   └── static/                    # 静态资源
│       ├── font/                  # 字体文件
│       └── img/                   # 图片资源
│
├── tests/                         # 测试文件
│   ├── conftest.py                # pytest 配置
│   ├── test_app.py                # App 测试
│   ├── test_auth.py               # 认证测试
│   ├── test_factory.py            # 工厂函数测试
│   └── test_post.py               # 帖子测试
│
├── config.py                      # 配置文件
├── setup.py                       # 安装配置
├── requirements.txt               # 依赖列表
├── ecosystem.config.js            # PM2 配置（可选）
└── README.md                      # 项目文档
```

## 🚀 快速开始

### 环境要求

- **Python**：3.7 或更高版本
- **MySQL**：5.7 或更高版本
- **Redis**：可选，用于缓存（推荐）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd ReadIO/Readio-Server
```

#### 2. 创建虚拟环境（推荐）

```bash
# 使用 venv
python3 -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置数据库

创建 MySQL 数据库：

```sql
CREATE DATABASE readio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 5. 配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# Flask 配置
export FLASK_APP=readio
export FLASK_ENV=development

# MySQL 配置
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=readio_db

# 服务器配置
export SERVER_IP=127.0.0.1:5000
export SECRET_KEY=your_secret_key
```

或直接修改 `config.py` 文件：

```python
SECRET_KEY = 'your_secret_key'
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'
MYSQL_DATABASE = 'readio_db'
```

#### 6. 初始化数据库

```bash
flask init-db
```

或手动执行 SQL 脚本：

```bash
mysql -u root -p readio_db < readio/database/init.sql
```

#### 7. 启动服务

```bash
# 开发环境
flask run

# 或指定端口
flask run --host=0.0.0.0 --port=5000
```

服务启动后，访问：http://localhost:5000

## 🔧 配置说明

### 数据库配置

在 `config.py` 或环境变量中配置：

```python
MYSQL_HOST = '127.0.0.1'      # MySQL 主机地址
MYSQL_PORT = 3306              # MySQL 端口
MYSQL_USER = 'root'            # MySQL 用户名
MYSQL_PASSWORD = 'password'    # MySQL 密码
MYSQL_DATABASE = 'readio_db'   # 数据库名
```

### 连接池配置

在 `readio/database/connectPool.py` 中配置连接池参数：

```python
# 连接池配置
pool_config = {
    'mincached': 5,      # 最小连接数
    'maxcached': 20,     # 最大连接数
    'maxshared': 10,     # 最大共享连接数
    'maxconnections': 50, # 最大连接数
    'blocking': True,    # 是否阻塞
    'maxusage': 0,       # 最大使用次数
    'setsession': []     # 会话设置
}
```

## 📡 API 接口

### 认证相关

- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册
- `GET /auth/profile` - 获取用户信息
- `POST /auth/logout` - 用户登出

### 书籍相关

- `GET /app/homepage/recommend` - 获取推荐内容
- `GET /app/bookshelf` - 获取书架列表
- `GET /app/book/detail/<book_id>` - 获取书籍详情
- `GET /app/book/read/<book_id>` - 获取阅读内容
- `POST /app/bookshelf/add` - 添加书籍到书架
- `POST /app/bookshelf/update` - 更新阅读进度

### 社区相关

- `GET /app/works` - 获取作品列表
- `POST /app/works/publish` - 发布作品
- `GET /app/post/<post_id>` - 获取帖子详情
- `POST /app/post/comment` - 发表评论

### 管理相关

- `GET /manage/user/list` - 用户列表
- `GET /manage/book/list` - 书籍列表
- `POST /manage/file/upload` - 文件上传
- `GET /monitor/server` - 服务器监控

详细 API 文档请参考项目设计文档。

## 🔐 认证机制

### Token 认证

系统使用 Token 进行用户认证：

1. 用户登录后，服务器生成 Token
2. 客户端在请求头中携带 Token：`Authorization: <token>`
3. 服务器验证 Token 有效性
4. Token 过期时间：24 小时（可配置）

### Token 管理

系统使用定时任务自动清理过期 Token：

```python
# 每小时检查一次，删除超过 1 天未活动的 Token
scheduler.add_job(
    func=checkSessionsAvailability,
    trigger='interval',
    seconds=3600
)
```

## 📁 文件处理

### 支持格式

- **EPUB**：使用 `ebooklib` 解析
- **TXT**：直接读取文本
- **MOBI**：使用 `mobi` 库解析
- **PDF**：使用 `pdfminer` 解析

### 文件抽象层

系统通过文件抽象层统一处理不同格式：

```python
# readio/utils/filechange.py
def read_book(file_path, file_type):
    """统一读取接口"""
    if file_type == 'epub':
        return read_epub(file_path)
    elif file_type == 'txt':
        return read_txt(file_path)
    # ...
```

## 🗄️ 数据库设计

### 主要表结构

- **users**：用户表
- **books**：书籍表
- **authors**：作者表
- **comments**：评论表
- **posts**：帖子表
- **works**：作品表
- **tags**：标签表
- **user_books**：用户书架关联表

详细数据库设计请参考 `readio/database/init.sql`。

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 显示详细输出
pytest -v

# 显示覆盖率
pytest --cov=readio
```

### 测试配置

测试配置在 `tests/conftest.py` 中：

```python
@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()
```

## 🚀 部署

### 开发环境

```bash
flask run
```

### 生产环境

#### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "readio:create_app()"
```

#### 使用 uWSGI

```bash
pip install uwsgi
uwsgi --http :5000 --module readio:create_app --callable app
```

#### 使用 PM2（Node.js 进程管理）

```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

#### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "readio:create_app()"]
```

```bash
docker build -t readio-server .
docker run -p 5000:5000 readio-server
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.readio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🔍 监控与日志

### 系统监控

访问 `/monitor/server` 获取服务器监控信息：

- CPU 使用率
- 内存使用情况
- 磁盘使用情况
- 系统负载

### 日志配置

Flask 默认日志配置，生产环境建议使用：

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'readio.log',
    maxBytes=10000,
    backupCount=1
)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

## 🐛 常见问题

### 1. 数据库连接失败

**问题**：无法连接到 MySQL 数据库

**解决方案**：
- 检查 MySQL 服务是否启动
- 验证数据库配置信息
- 确认数据库用户权限

### 2. 文件上传失败

**问题**：上传大文件时失败

**解决方案**：
- 检查文件大小限制
- 确认上传目录权限
- 增加请求超时时间

### 3. Token 验证失败

**问题**：Token 验证总是失败

**解决方案**：
- 检查 Token 格式
- 确认 Token 未过期
- 验证 SECRET_KEY 配置

## 📝 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 使用类型提示（Type Hints）
- 添加文档字符串（Docstrings）

### 模块设计

- 每个功能模块使用 Blueprint
- 工具函数放在 `utils` 模块
- 数据库操作统一管理

### 错误处理

使用自定义异常：

```python
from readio.utils.myExceptions import ReadioException

try:
    # 业务逻辑
except Exception as e:
    raise ReadioException("错误信息")
```

## 📚 参考文档

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [MySQL 文档](https://dev.mysql.com/doc/)
- [APScheduler 文档](https://apscheduler.readthedocs.io/)

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

Copyright (c) 2023 ReadIO

详情请参阅 [LICENSE](LICENSE) 文件。

## 📮 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。

---

**ReadIO 后端服务** - 稳定、高效、可靠
