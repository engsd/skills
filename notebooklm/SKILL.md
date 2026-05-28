---
name: notebooklm
description: |
  使用 Google NotebookLM 管理笔记本、生成内容、对话问答。当用户提到以下需求时使用此技能：
  (1) 查看/管理笔记本 (2) 添加/删除来源 (3) 生成播客/视频/测验/闪卡/思维导图 
  (4) 询问笔记本内容 (5) 下载生成的内容 (6) 与笔记本对话
---

# NotebookLM 技能

使用 `notebooklm-py` 项目管理 Google NotebookLM。

## 项目路径

```
D:\git-project\notebooklm-py
```

## 使用方式

所有命令在以下目录执行：
```
cd D:\git-project\notebooklm-py
.venv\Scripts\notebooklm.exe
```

## 常用命令

### 认证
```bash
.venv\Scripts\notebooklm login   # 首次登录
```

### 笔记本管理
```bash
.venv\Scripts\notebooklm list                              # 列出所有笔记本
.venv\Scripts\notebooklm use <id或标题>                     # 选择当前笔记本
.venv\Scripts\notebooklm status                            # 查看当前笔记本
.venv\Scripts\notebooklm create "标题"                     # 创建笔记本
.venv\Scripts\notebooklm delete <id>                      # 删除笔记本
.venv\Scripts\notebooklm rename <id> "新标题"             # 重命名
```

### 来源管理
```bash
.venv\Scripts\notebooklm source list                       # 列出当前笔记本的来源
.venv\Scripts\notebooklm source add <nb-id> <url>         # 添加URL来源
.venv\Scripts\notebooklm source add-drive <nb-id>         # 添加Google Drive
.venv\Scripts\notebooklm source add-research <nb-id>      # 添加研究来源
.venv\Scripts\notebooklm source refresh <nb-id>           # 刷新来源
.venv\Scripts\notebooklm source fulltext <nb-id>          # 获取来源全文
```

### 对话问答
```bash
.venv\Scripts\notebooklm ask "问题"                        # 询问当前笔记本
.venv\Scripts\notebooklm history                          # 获取对话历史
```

### 内容生成
```bash
.venv\Scripts\notebooklm generate audio                    # 生成播客(Audio Overview)
.venv\Scripts\notebooklm generate video                   # 生成视频(Video Overview)
.venv\Scripts\notebooklm generate quiz                    # 生成测验
.venv\Scripts\notebooklm generate flashcards              # 生成闪卡
.venv\Scripts\notebooklm generate mind-map                # 生成思维导图
.venv\Scripts\notebooklm generate slide-deck               # 生成幻灯片
.venv\Scripts\notebooklm generate infographic              # 生成信息图
.venv\Scripts\notebooklm generate data-table               # 生成数据表
.venv\Scripts\notebooklm generate report                  # 生成报告
```

### 内容下载
```bash
.venv\Scripts\notebooklm download audio                   # 下载播客
.venv\Scripts\notebooklm download video                   # 下载视频
.venv\Scripts\notebooklm download quiz                    # 下载测验
.venv\Scripts\notebooklm download flashcards              # 下载闪卡
.venv\Scripts\notebooklm download mind-map                # 下载思维导图
```

## 使用示例

1. **查看笔记本列表**
   ```bash
   cd D:\git-project\notebooklm-py; .venv\Scripts\notebooklm list
   ```

2. **选择笔记本**
   ```bash
   cd D:\git-project\notebooklm-py; .venv\Scripts\notebooklm use 初中英语
   ```

3. **询问问题**
   ```bash
   cd D:\git-project\notebooklm-py; .venv\Scripts\notebooklm ask "总结这个笔记本的主要内容"
   ```

4. **生成播客**
   ```bash
   cd D:\git-project\notebooklm-py; .venv\Scripts\notebooklm generate audio
   ```

5. **下载内容**
   ```bash
   cd D:\git-project\notebooklm-py; .venv\Scripts\notebooklm download audio
   ```

## Python API

如需更复杂的操作，可以使用 Python API：

```python
import asyncio
from notebooklm import NotebookLMClient

async def main():
    async with await NotebookLMClient.from_storage() as client:
        # 列出笔记本
        nbs = await client.notebooks.list()
        for nb in nbs:
            print(f"{nb.id} - {nb.title}")
        
        # 获取来源
        sources = await client.sources.list(nb.id)
        
        # 问答
        result = await client.chat.ask(nb.id, "问题")
        print(result.answer)

asyncio.run(main())
```

运行方式：
```bash
cd D:\git-project\notebooklm-py
.venv\Scripts\python your_script.py
```
