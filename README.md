# MitmProxy 桌面控制面板

这是一个基于 mitmproxy 的图形化桌面控制面板，提供了友好的用户界面来管理和监控网络请求。

## 功能特性

- 图形化界面控制 mitmproxy
- 实时日志显示
- 数据收集和统计
- 飞书表格集成
- MongoDB 数据存储

## 系统要求

- Python 3.7+
- 支持的操作系统: Windows, macOS, Linux

## 安装步骤

1. 克隆项目:
   ```
   git clone <repository-url>
   cd wechat_mitm
   ```

2. 创建虚拟环境:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或者
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

4. 配置环境变量:
   创建 `.env` 文件并配置以下参数:
   ```
   # MongoDB配置
   MONGODB_HOST=8.138.164.134
   MONGODB_PORT=27017
   MONGODB_DATABASE=netbar_data
   MONGODB_USERNAME=admin
   MONGODB_PASSWORD=your_password
   
   # 飞书配置
   FEISHU_APP_ID=your_app_id
   FEISHU_APP_SECRET=your_app_secret
   FEISHU_DOMAIN=https://open.feishu.cn
   ```

5. 运行应用:
   ```
   python main.py
   ```

## 打包为桌面应用

项目支持打包为独立的桌面应用，可以按照以下步骤操作：

1. 确保已安装所有依赖:
   ```
   pip install -r requirements.txt
   ```

2. 运行打包脚本:
   ```
   python build_app.py
   ```

3. 打包完成后，可在 `dist/mitmproxy_desktop` 目录找到可执行文件

### 打包注意事项

- 打包后的应用需要在同一目录下保留 `.env` 配置文件
- 应用会在运行目录生成日志文件 (`app.log`)
- 不同操作系统打包的结果不通用，需要在对应系统上重新打包

## 项目结构

```
.
├── config/                 # 配置文件
│   └── settings.py         # 应用配置
├── core/
│   ├── scripts/            # 脚本文件
│   ├── ui/                 # 用户界面
│   │   ├── controllers/    # 控制器
│   │   └── views/          # 视图组件
│   └── utils/              # 工具类
├── main.py                 # 应用入口
├── requirements.txt        # 依赖列表
└── build_app.py            # 打包脚本
```

## 开发说明

### 环境变量配置

项目使用 `.env` 文件管理敏感配置信息，包括数据库连接和第三方服务密钥。

### 日志记录

应用会同时输出日志到控制台和文件，默认日志级别为 INFO。

## 常见问题

Q: 打包后的应用无法运行？
A: 确保 `.env` 配置文件与可执行文件在同一目录下。

Q: 出现权限问题？
A: 在 macOS/Linux 上可能需要为可执行文件添加执行权限: `chmod +x mitmproxy_desktop`

## 许可证

[待补充]