# 🔥 GitHub 热门项目洞察机器人

GitHub热门项目洞察机器人是一个自动化工具，用于抓取、分析并生成GitHub近期热门项目的详细报告。通过GitHub API获取数据，结合AI智能分析（DeepSeek），生成包含项目排名、技术亮点和趋势变化的综合报告，帮助开发者快速掌握技术动态。

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ 主要特性

- **智能趋势分析** - 自动获取GitHub近期热门项目，分析编程语言分布和项目趋势
- **AI驱动洞察** - 集成DeepSeek AI生成项目技术亮点和核心价值分析
- **多格式报告** - 生成控制台报告和Markdown格式的详细报告
- **历史对比** - 支持与历史数据对比，展示项目排名变化和趋势演进
- **缓存优化** - 自动缓存项目README，避免重复请求提高效率

## 🚀 快速开始

### 环境要求
- Python 3.7+
- GitHub个人访问令牌（需要public_repo权限，用于访问公开仓库）
- DeepSeek API密钥（可选，用于AI分析）

### 安装步骤
1. 克隆仓库：
```bash
git clone https://github.com/JuhaZh/github-insight-bot.git
cd github-insight-bot
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置环境变量：
```bash
# Windows PowerShell
$env:GITHUB_TOKEN="your_github_token"
$env:DEEPSEEK_API_KEY="your_deepseek_key"  # 可选

# Linux/macOS
export GITHUB_TOKEN="your_github_token"
export DEEPSEEK_API_KEY="your_deepseek_key"  # 可选
```

4. 运行程序：
```bash
python github_trending_bot.py
```

## 📖 使用方法

### 基本使用
运行程序后，按提示输入：
- 查询天数（默认7天）
- 项目数量（默认10个）

程序将：
1. 获取GitHub热门项目
2. 使用AI生成项目分析
3. 保存原始数据到`data/`目录
4. 生成Markdown报告到`reports/`目录

### 高级配置
通过环境变量配置：
- `GITHUB_TOKEN`: GitHub个人访问令牌（必需）
- `DEEPSEEK_API_KEY`: DeepSeek API密钥（启用AI分析）

程序生成的报告包含：
- 项目排行榜（名称、作者、星标数等）
- 编程语言分布统计
- AI生成的项目技术分析
- 历史趋势对比（当有历史数据时）

## 📊 示例输出

### 控制台输出示例
```
🔥 GitHub 热门项目洞察机器人
请输入查询天数 (默认7天): 7
请输入项目数量 (默认10个): 5
正在获取最近7天的Top 5热门项目...
⏳ 开始处理 5 个项目的AI总结...
生成AI总结: 100%|██████████| 5/5 [00:15<00:00,  3.12s/it]
✅ 原始数据已保存: data/data_2025-07-31.json
✅ Markdown报告已保存: reports/github_trending_7days_2025-07-31.md
```

查看`reports/`目录下的Markdown报告文件，示例报告包含：

```markdown
# 🔥 GitHub 热门项目洞察报告

**查询时间：** 2025年07月31日  
**时间范围：** 最近7天  
**项目数量：** 10个

## 🏆 热门项目排行榜

| 排名 | 📦 项目名称 | 👤 作者 | ⭐ Star | 🍴 Fork | 语言 | 📝 描述 |
|------|----------|------|--------|--------|------|------|
| 1 | [agents](https://github.com/contains-studio/agents) | [contains-studio](https://github.com/contains-studio) | ⭐ 3958 | 🍴 717 | N/A | sharing current agents in use<br>> 🤖 **AI小结**:<br>- 🎯 核心功能：提供模块化AI代理集合，加速开发全流程自动化<br>- 💡 技术亮点：基于Claude Code的代理系统，YAML+Markdown结构化配置<br>- 🔥 火爆原因：契合AI代理协作趋势，开箱即用的专业领域解决方案 |
...

## 📊 编程语言分布
| 语言 | 项目数量 |
|------|----------|
| N/A | 6个项目 |
| Python | 2个项目 |
...
```

## 🏗️ 项目结构

```
github-insight-bot/
├── data/                  # 原始数据存储（JSON格式）
│   └── data_2025-07-31.json
├── reports/               # 生成的Markdown报告
│   └── github_trending_7days_2025-07-31.md
├── readme_cache/          # README缓存
│   └── contains-studio__agents.md
├── github_trending_bot.py # 主程序
├── requirements.txt       # Python依赖
└── README.md              # 项目文档
```

## ❓ 常见问题

### Q: 为什么需要GitHub Token？
A: 用于调用GitHub API获取项目数据，避免频率限制。

### Q: 不设置DeepSeek API Key会怎样？
A: 程序仍可正常运行，但不会生成AI项目分析。

### Q: 数据多久更新一次？
A: 每次手动运行都会获取最新数据，README缓存有效期7天。

## 🤝 参与贡献

欢迎贡献！请遵循以下流程：
1. Fork 本仓库
2. 创建新分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

## 📄 开源协议

本项目采用 [MIT 许可证](LICENSE)，您可以自由使用、修改和分发代码。
