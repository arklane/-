### 项目结构

```
fund-website/
│
├── public/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── scripts.js
│   └── index.html
│
├── routes/
│   └── api.js
│
├── server.js
└── package.json
```

### 1. 初始化项目

在项目目录中，运行以下命令来初始化Node.js项目：

```bash
npm init -y
npm install express body-parser cors
```

### 2. 创建服务器 (server.js)

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const apiRoutes = require('./routes/api');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

app.use('/api', apiRoutes);

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
```

### 3. 创建API路由 (routes/api.js)

```javascript
const express = require('express');
const router = express.Router();

// 示例基金数据
const funds = [
    {"代码":"540007","简称":"汇丰晋信中小盘股","基金经理":"郑小兵","基金公司":"汇丰晋信"},
    {"代码":"001097","简称":"华泰柏瑞积极优选","基金经理":"王林军","基金公司":"华泰柏瑞"},
    // 添加更多基金数据...
];

// 获取所有基金
router.get('/funds', (req, res) => {
    res.json(funds);
});

// 根据代码查找基金
router.get('/funds/:code', (req, res) => {
    const fund = funds.find(f => f.代码 === req.params.code);
    if (fund) {
        res.json(fund);
    } else {
        res.status(404).send('基金未找到');
    }
});

module.exports = router;
```

### 4. 创建前端页面 (public/index.html)

```html
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/styles.css">
    <title>基金网站</title>
</head>
<body>
    <header>
        <h1>基金推荐平台</h1>
        <nav>
            <ul>
                <li><a href="#home">首页</a></li>
                <li><a href="#recommendations">热门基金推荐</a></li>
                <li><a href="#search">基金信息查找</a></li>
                <li><a href="#settings">个人设置</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section id="home">
            <h2>欢迎来到基金推荐平台</h2>
            <p>这里是您的投资助手。</p>
        </section>

        <section id="recommendations">
            <h2>热门基金推荐</h2>
            <div id="fund-list"></div>
        </section>

        <section id="search">
            <h2>基金信息查找</h2>
            <input type="text" id="fund-code" placeholder="输入基金代码">
            <button id="search-button">查找</button>
            <div id="fund-info"></div>
        </section>

        <section id="settings">
            <h2>个人设置</h2>
            <p>在这里您可以设置个人信息。</p>
        </section>
    </main>

    <footer>
        <p>&copy; 2023 基金推荐平台</p>
    </footer>

    <script src="js/scripts.js"></script>
</body>
</html>
```

### 5. 添加样式 (public/css/styles.css)

```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

header {
    background-color: #4CAF50;
    color: white;
    padding: 10px 0;
    text-align: center;
}

nav ul {
    list-style-type: none;
    padding: 0;
}

nav ul li {
    display: inline;
    margin: 0 15px;
}

main {
    padding: 20px;
}

footer {
    text-align: center;
    padding: 10px 0;
    background-color: #f1f1f1;
    position: relative;
    bottom: 0;
    width: 100%;
}
```

### 6. 添加交互功能 (public/js/scripts.js)

```javascript
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/funds')
        .then(response => response.json())
        .then(data => {
            const fundList = document.getElementById('fund-list');
            data.forEach(fund => {
                const div = document.createElement('div');
                div.textContent = `${fund.简称} (${fund.代码}) - 基金经理: ${fund.基金经理}`;
                fundList.appendChild(div);
            });
        });

    document.getElementById('search-button').addEventListener('click', () => {
        const code = document.getElementById('fund-code').value;
        fetch(`/api/funds/${code}`)
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('基金未找到');
                }
            })
            .then(data => {
                const fundInfo = document.getElementById('fund-info');
                fundInfo.textContent = `基金名称: ${data.简称}, 基金经理: ${data.基金经理}, 基金公司: ${data.基金公司}`;
            })
            .catch(error => {
                document.getElementById('fund-info').textContent = error.message;
            });
    });
});
```

### 7. 启动服务器

在项目目录中，运行以下命令启动服务器：

```bash
node server.js
```

### 8. 访问网站

打开浏览器，访问 `http://localhost:3000`，您将看到创建的基金推荐平台。

### 总结

这个项目是一个简单的基金推荐网站，包含了主界面、热门基金推荐、基金信息查找和个人设置界面。您可以根据需要扩展功能和样式。