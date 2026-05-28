---
name: Obsidian-code
description: Turn a code project into an Obsidian-friendly learning vault with bidirectional links, data-flow explanations, beginner-friendly walkthroughs, and per-file study notes. Use this skill whenever the user wants to read a project through Obsidian, asks for code-to-markdown documentation, wants a project turned into linked notes, requests data-flow or lifecycle explanations, or wants a beginner-friendly map of how code works.
---

# Obsidian-code

Use this skill to convert a codebase into an Obsidian-style study system. The goal is not to copy source code, but to help the user understand how the project works through linked notes, data flow, and beginner-friendly explanations.

## What this skill produces

This skill usually creates an `ob/` directory inside the target project and fills it with linked Markdown notes.

Typical outputs:
- `PROJECT_FLOW.md`
- `FILE_INDEX.md`
- `DATA_BIRTH.md`
- `FLOW_*.md`
- `BUTTON_ACTIONS.md`
- one `original-file-name.ext.md` note for each important handwritten source file

## When to use this skill

Use it when the user asks for any of the following:
- turn this project into Obsidian notes
- make this code easier to study
- explain how the data flows through the project
- explain where the data comes from and where it goes
- create linked markdown docs for the important files
- make a beginner-friendly map of this codebase

Use it even if the user does not explicitly mention Obsidian, as long as they want a navigable Markdown knowledge base for understanding a project.

## Core principles

1. Do not dump raw code unless the user explicitly wants that.
2. Preserve the original file names in note names so the user can map notes back to source quickly.
3. Prefer understanding over exhaustiveness.
4. Explain both the technical truth and the beginner-friendly intuition.
5. Use bidirectional links aggressively so the user never loses their place.
6. Focus on handwritten logic, not scaffolding or generated files.

## Default output structure

Create notes like this by default:

```txt
ob/
  PROJECT_FLOW.md
  FILE_INDEX.md
  DATA_BIRTH.md
  BUTTON_ACTIONS.md
  BIRTH_*.md
  FLOW_*.md
  App.tsx.md
  appReducer.ts.md
  promptService.ts.md
  ...
```

## Default exclusions

Unless the user asks otherwise, skip:
- `node_modules/`
- `dist/`
- build outputs
- lockfiles
- assets with no logic
- icon files
- obvious template or config files that do not help explain the program

Include configs only when they materially affect behavior.

## Workflow

### 1. Read the project before writing notes

Inspect:
- app entry points
- routing
- global state
- services or utilities
- important pages and components
- types
- default data
- storage or API boundaries

First determine whether the project is:
- function-driven
- component-driven
- event-driven
- state-driven
- API-driven

Most modern frontend projects are mixed, so note the dominant pattern rather than forcing a false simplification.

### 2. Separate handwritten logic from scaffolding

Prioritize files that actually teach the project:
- source files with behavior
- state management
- business logic
- forms
- storage
- domain types

Downgrade or skip:
- generated output
- static assets
- boilerplate configs
- template leftovers no longer used

If you notice dead or old code, mention it clearly instead of silently blending it into the main flow.

### 3. Build the top-level navigation first

Create:

#### `PROJECT_FLOW.md`
This is the big-picture map.

Cover:
- where the app starts
- where state comes from
- where user input enters
- where business data is created
- how data is transformed
- where it is rendered
- where it is persisted

#### `FILE_INDEX.md`
This is the category-based index.

Organize by groups such as:
- entry
- state management
- pages
- components
- services
- types and data
- data birth
- data flow

### 4. Add “data birth” before “data flow”

Beginners often get stuck before they understand where objects come from. Solve that first.

Create:
- `DATA_BIRTH.md`
- `BIRTH_默认数据怎么来.md`
- `BIRTH_新建X怎么生成.md`
- `BIRTH_编辑为什么会生成新状态.md`
- `BIRTH_localStorage里的数据怎么回来.md`

Adjust the exact names to the project domain when needed.

For each data-birth note, explain:
- what existed before
- what code receives it
- what new data gets created
- what fields were added or changed
- why that transformation exists

Always include both:
- `专业解释`
- `白话解释`

### 5. Add business-flow notes

Create `FLOW_*.md` notes for the main user journeys.

Typical flows:
- initialization
- create
- edit
- delete
- filter/search
- settings
- persistence

Each flow note should answer:
- what starts the flow
- what data enters
- what functions or components touch it
- what state changes
- what the user sees at the end

### 6. Add button-oriented beginner notes

Create `BUTTON_ACTIONS.md`.

This note should explain the project from the user’s action perspective:
- click create
- click edit
- click delete
- click favorite
- type in search
- change theme

For each action, walk through:
1. where the event starts
2. what handler runs
3. what data is produced
4. what action is dispatched
5. what reducer or service runs
6. what state changes
7. what UI updates
8. what gets persisted

This note is especially valuable for beginners. Keep it direct and concrete.

### 7. Create one note per important source file

Name each note as:
- `OriginalFileName.ext.md`

Examples:
- `App.tsx.md`
- `appReducer.ts.md`
- `promptService.ts.md`

Do not rename them into abstract titles unless the user asks.

### 8. Use this file template

For each per-file note, use a structure close to this:

```md
[[PROJECT_FLOW.md]]
[[FILE_INDEX.md]] > 某个分类

# App.tsx
类型: 文件

## 导出项
- `App`
  - 类型: 组件
  - 作用: ...

## 数据输入
- ...

## 数据产生
- ...

## 数据输出
- ...

## 上游
- ...

## 下游
- ...

## 专业解释
- ...

## 白话解释
- ...
```

Adjust the content to the file. If a file has no real data transformation, say so plainly.

## Naming rules for symbols

Always tell the user what each important name is:
- component
- page component
- hook
- reducer
- utility function
- type definition
- constant
- derived data
- local state
- event handler

Do not make the user infer this from context.

## Link rules

Every note should make orientation easy.

At minimum, place near the top:
- `[[PROJECT_FLOW.md]]`
- `[[FILE_INDEX.md]] > category`

Then add links to related notes throughout the body.

The user should always be able to answer:
- where am I
- what does this file do
- what data comes in
- what data comes out
- where should I click next

## Explanation style

For important logic, provide both:

### 专业解释
State what the code is doing accurately using correct engineering language.

### 白话解释
Explain the same idea in ordinary language without dumbing it down into nonsense.

Use this pairing especially for:
- reducers
- service functions
- data creation
- persistence
- derived state
- event handling

## What not to do

- do not paste entire source files by default
- do not write fake explanations for files you did not inspect
- do not treat template files as core logic
- do not flatten the whole project into “just functions” if it clearly uses state, routing, or components
- do not lose the distinction between original data, derived data, and persisted data

## Good defaults for frontend projects

If the project is a React-style app, make sure to explain:
- app bootstrap
- provider/context setup
- reducer and actions
- form input collection
- service-layer transformations
- derived list filtering
- localStorage persistence
- route-based rendering

## Expected final result

When this skill works well, the user should be able to:
- open `PROJECT_FLOW.md` and understand the whole app at a glance
- jump into any file note and know what role it plays
- follow one feature end to end
- understand where data is born, changed, rendered, and saved
- learn the project even if they are still a beginner

## Example prompts this skill should handle

Example 1:
Input: “Read this frontend project and turn only the handwritten core logic into Obsidian-linked notes so I can study it.”
Output: an `ob/` knowledge vault with flow notes, file notes, and beginner-friendly explanations.

Example 2:
Input: “I want to understand where state comes from and how clicking this button changes the UI.”
Output: data-birth notes, action-flow notes, and file notes with upstream/downstream links.

Example 3:
Input: “Don’t copy the whole code. Keep the file names, but explain the functions, components, and data flow.”
Output: per-file Markdown notes that preserve file names and explain symbols by role.
