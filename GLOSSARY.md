# GLOSSARY

本仓库 spec、ticket、ADR 和 agent 输出中使用的术语。写这些文档时用这里的定义，不要临时换同义词。

## issue

存在 GitHub Issues 里、可被讨论和关闭的工作单元。一个 issue 可能是一个 spec、一个 ticket，或一条普通讨论。

不要用：任务、单子、工单。

## ticket

由 `$to-tickets` 从 spec 或计划拆出的 tracer-bullet 工作单元，一个 ticket 就是一条 issue。ticket 必须能被独立验证，并声明 blocking 关系。

不要用：子任务、卡片。

## spec

对「要解决什么问题、怎么解决、验收标准是什么」的完整描述，通常是一条打了 `ready-for-agent` 的 issue。spec 不做访谈，只综合已有讨论。

不要用：需求文档、PRD。

## triage role

issue 在分类与流转中扮演的角色，分两类：category role（`bug`、`enhancement`）和 state role（`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`）。

不要用：状态、优先级。

## triage label

tracker 上承载 triage role 的标签字符串。本仓库直接用 role 名作标签名，映射见 `docs/agents/triage-labels.md`。

不要用：tag。

## domain doc

描述领域语言和架构决策的文档，即 `GLOSSARY.md` 与 `docs/adr/`。agent 在探索代码前应先读，缺失时不提示、不预先创建。

不要用：项目文档、wiki。

## ADR

Architecture Decision Record，一条决策一份，放在 `docs/adr/`，从 `0001` 起顺序编号，包含 Status、Context、Decision、Consequences。

不要用：设计文档、决策记录表。

## seam

测试可以切入的边界。优先复用已有 seam；新 seam 只在必要时、且尽量靠外层新增。理想数量是一个。

不要用：切口、钩子。

## tracer bullet

贯穿每一层、窄但完整的一条实现路径，完成后可独立演示或验证。ticket 的基本单位。

不要用：原型、骨架。

## vertical slice

按 tracer bullet 原则切出的工作切片，横跨 schema、API、UI、测试，而不是只做某一层。wide refactor 是唯一例外，按 expand–contract 排序。

不要用：模块、分层任务。

## blocker

gate 住某个 ticket 的其他 ticket。GitHub 上用 native issue dependency 表示，全部关闭后该 ticket 才进入 frontier。

不要用：依赖、前置任务。

## frontier

当前可以立刻开工的 ticket 集合：未被关闭、没有未完成 blocker、没有 assignee。按 ticket 编号取第一个。

不要用：待办队列。

## agent brief

triage 时写下的、给后续 agent 的持久说明，包含上下文、约束和验收方式，让接手者不必重读整段对话。

不要用：交接说明、prompt。
