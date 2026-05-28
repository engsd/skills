# skills

这是我的 Codex skills 备份与分享仓库。

仓库目标：
- 备份我当前在 `C:\Users\eng\.codex\skills` 下使用的主要技能
- 方便在不同 AI 工作流之间复用
- 方便公开整理、持续迭代和分享

说明：
- 本仓库默认收录 `C:\Users\eng\.codex\skills` 下的非 `.system` 技能目录
- `.system` 属于系统内置技能集合，这次没有放进仓库
- 复制时排除了各技能目录中的 `.git` 元数据，只保留技能内容本身

## 仓库结构

每个顶级目录通常对应一个 skill。

部分目录是“单技能”：
- 例如 `Obsidian-code`、`humanizer`、`pi-executor`

部分目录是“技能合集”：
- 例如 `frontend-design`
- 这类目录内部还会继续包含多个子技能

## 技能说明

### 1. `Obsidian-code`
作用：
- 把代码项目整理成适合 Obsidian 阅读的双链知识库
- 不主打抄源码，而是主打理解项目如何运作

典型产出：
- `PROJECT_FLOW.md`
- `FILE_INDEX.md`
- `DATA_BIRTH.md`
- `BUTTON_ACTIONS.md`
- 各核心源文件对应的 `原文件名.md`

适用场景：
- 想把项目整理成学习笔记
- 想看懂数据从哪里来、怎么处理、最后到哪里
- 想把代码解释成适合初学者阅读的文档

### 2. `claude-flow`
作用：
- 让当前 AI 作为规划者和监督者
- 把较长、较复杂的实现工作交给 Claude Code 执行

适用场景：
- 需要分工协作
- 需要 Claude Code 作为执行工人持续推进任务
- 需要当前 AI 保留决策、验收和中断处理职责

### 3. `frontend-design`
作用：
- 一个前端与文档产物相关的技能合集
- 不只是单一 skill，而是一整套前端、文档、演示、构建相关技能集合

包含的子技能方向：
- `frontend-design`：高质量前端页面与界面设计
- `internal-comms`：内部沟通类内容产出
- `mcp-builder`：构建 MCP 服务
- `skill-creator`：创建和迭代 skill
- `theme-factory`：为产物补充主题系统
- `web-artifacts-builder`：构建更复杂的 Web artifact
- `webapp-testing`：Web 应用测试
- `pdf` / `docx` / `pptx` / `xlsx`：文档与 Office 产物相关流程

适用场景：
- 做前端页面
- 做复杂 HTML/文档产物
- 做风格化输出
- 做技能开发与相关工程化任务

### 4. `hatch-pet`
作用：
- 生成、修复、验证、打包 Codex 兼容的动画宠物与 spritesheet

适用场景：
- 做桌面宠物
- 做角色动画小精灵
- 做品牌 mascot 风格的小型可动形象

### 5. `html-anything`
作用：
- 把文本回答、文件、文件夹、URL 或导出结果，转换成一个精致的单文件 HTML 页面

适用场景：
- 想把一段分析结果变网页
- 想把目录/数据/URL 变成可浏览的 HTML 展示
- 想做轻量分享页面

### 6. `humanizer`
作用：
- 去掉 AI 味，把文本改得更自然、更像人写的

适用场景：
- 润色文章
- 改写 AI 文案
- 优化内部沟通、公众号、说明文等内容的自然度

### 7. `image-workflow`
作用：
- 把文章拆段并批量转成配图工作流
- 支持占位符插图和图片链接替换

适用场景：
- 文章生图
- 内容配图流水线
- 需要一篇文章对应多张 AI 图片时

### 8. `karpathy-guidelines`
作用：
- 提供一套更稳健的编码行为准则
- 帮助减少 LLM 在写代码时常见的过度设计和跑偏问题

适用场景：
- 写代码
- 重构代码
- 做 code review
- 希望输出更克制、更可验证的工程结果

### 9. `n8n-skills`
作用：
- n8n 工作流构建总入口技能
- 覆盖节点配置、表达式、代码节点、验证、调试和常见模式

适用场景：
- 构建 n8n 工作流
- 调试 n8n 节点
- 写 n8n Code 节点逻辑
- 处理 HTTP、AI、数据库、定时任务等自动化流程

### 10. `notebooklm`
作用：
- 使用 Google NotebookLM 管理笔记本、来源、问答和内容生成

适用场景：
- 管理 NotebookLM 笔记本
- 添加或删除来源
- 生成播客、视频、闪卡、测验、思维导图
- 基于已有资料进行问答

### 11. `pi-executor`
作用：
- 让 Pi 作为执行 worker 承担真实项目工作
- 当前 AI 负责规划、监督、兜底和验收

适用场景：
- 想通过 Pi 持续推进代码、写作、调试、重构任务
- 想保留跨会话执行连续性

### 12. `playwright`
作用：
- 通过终端驱动真实浏览器自动化

适用场景：
- 打开页面
- 自动填写表单
- 截图
- 抓取页面数据
- 调试前端 UI 行为

### 13. `restrained-literary-wechat-writing`
作用：
- 以克制、有人味、带书卷气但不做作的风格写公众号文章

适用场景：
- 公众号文章改写
- 人文历史类文章
- 文化评论
- 人物故事、读书随笔

### 14. `web-video-presentation`
作用：
- 把文章或口播稿做成“看起来像视频”的网页演示
- 可以进一步用于录屏、口播展示或视频化表达

适用场景：
- 教程录屏
- 产品讲解
- 视频号 / B站 / YouTube 风格网页演示
- 用网页做“动态 PPT 但不像 PPT”的内容

## 如何使用这些技能

通常每个 skill 目录中最重要的是：
- `SKILL.md`

有些 skill 还会带：
- `scripts/`
- `references/`
- `assets/`
- `examples/`

理解顺序建议：
1. 先看该技能目录下的 `SKILL.md`
2. 再看它引用的 `references/` 或 `examples/`
3. 最后根据需要运行 `scripts/`

## 后续计划

我会继续把这个仓库整理得更适合复用，包括但不限于：
- 补充每个 skill 的中文简介
- 给核心 skill 增加测试样例
- 整理 skill 之间的关系图
- 标注哪些是我自定义的，哪些是外部引入后本地使用的
