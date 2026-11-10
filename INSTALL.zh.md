# 安装 cwiki（wiki-management skill）

> 中文（默认） | [English](INSTALL.md) — 如有出入以英文版为准。

逐步安装、验证、升级与排障。速览版在 [README § 安装](README.md#安装)，本文是详细版。

## 0. 前置条件

- **Claude Code**（CLI、桌面应用或 IDE 扩展），带 skills 支持——近期任何版本都会自动列出用户级与项目级 skill。
- **git**（clone 类安装需要；下面的模式 C 无需 git）。
- 无需构建、无需 pip install：skill 就是纯 markdown + 可选的纯标准库 Python 工具。

两条支配下文一切的事实：

1. **文件夹名就是 skill 名。** 装到 `.../skills/wiki-management/` 得到的 skill 就叫 `wiki-management`。想换名字改文件夹即可——内部没有任何东西依赖这个名字。
2. **skill 在会话启动时加载。** 装完或升级后要开**新**会话；跑着的会话看不到它。

## 1. 选安装模式

| 模式 | 位置 | 可见范围 | 适用 |
|---|---|---|---|
| A — 用户全局 | `~/.claude/skills/wiki-management/` | 本机所有项目 | 想到处都能用这套方法论（最常见） |
| B — 项目内 | `<项目>/.claude/skills/wiki-management/` | 仅该项目，**且所有 clone 该项目的人** | wiki 约定要随仓库走 / 团队共用 |
| C — 无 git 拷贝 | 与 A 或 B 相同路径 | 同上 | 没有 git 的机器，或想要冻结快照 |

模式 A 与 B 可共存；项目级同名 skill 会在该项目内**遮蔽**用户全局的——这正是"项目钉住特定版本、全局保持最新"的做法。

### 模式 A —— 用户全局

```powershell
# Windows (PowerShell)
git clone https://github.com/chenlei1700/cwiki "$env:USERPROFILE\.claude\skills\wiki-management"
```

```bash
# macOS / Linux
git clone https://github.com/chenlei1700/cwiki ~/.claude/skills/wiki-management
```

### 模式 B —— 项目内

```bash
cd <你的项目>
git clone https://github.com/chenlei1700/cwiki .claude/skills/wiki-management
```

若你的项目本身是 git 仓库，要决定 skill 以什么方式随行：

- **Vendored（团队推荐）**：删掉 skill 自己的 git 元数据、把文件提交进项目——所有 clone 项目的人零步骤获得 skill：

  ```bash
  rm -rf .claude/skills/wiki-management/.git
  git add .claude/skills/wiki-management && git commit -m "vendor wiki-management skill"
  ```

- **Submodule**：`git submodule add https://github.com/chenlei1700/cwiki .claude/skills/wiki-management` —— 保持可用 git 升级，但每个协作者都得记得 `git submodule update --init`。只有更新频繁时才值得。

- 既不 vendor 也不 submodule 地提交一个嵌套 clone，协作者拿到的是**空目录**——别这么发。

### 模式 C —— 无 git 拷贝

下载仓库归档（GitHub → Code → Download ZIP 或 release 包），解压后放到模式 A/B 的路径。**记下你拷的是哪个 commit/版本**（README 更新日志有写）——纯文件夹拷贝没法 `git pull`，升级只能重拷（见 §4）。

## 2. 验证安装

1. 在任意项目开一个**新** Claude Code 会话。
2. skill 应出现在可用 skill 列表（名字 `wiki-management`，或你改的文件夹名）。也可以直接问：*"你能看到 wiki-management skill 吗？"*
3. 不碰真实项目的功能冒烟：在一个空的临时目录说 `bootstrap wiki`——应当得到一个领域目录问题，然后生成 `wiki/` 骨架。完事删掉临时目录。

skill 没出现 → 见 §5 排障。

## 3. 装了什么、没装什么

安装 skill 给 Claude 的是**方法论**（skill.md、templates、docs）。两样东西刻意**不会**自动生效：

- **维护工具**（`tools/*.py`）是参考实现，不是自动运行的服务。用法：拷进你的项目（惯例 `scripts/maintenance/`），改标记好的 CONFIG 块，跑一遍 `--selftest`，再按 [tools/README.md](tools/README.md) 接进 pre-commit / hooks / 夜间任务。`wiki_lint_skeleton.py` 第一周先 report-only，再给 exit code。
- **规模件**（SCHEMA §9–§16）在各自书面的采纳触发条件满足前保持休眠。首日全装是文档里写明的反模式，不是捷径。

然后按你的场景说第一句话（README § 使用）：全新项目 `bootstrap wiki`，已有文档的项目 `adopt wiki`。

## 4. 升级

- **clone 安装（A/B）**：在 skill 文件夹里 `git pull`，然后开新会话。看 README 更新日志里有没有值得采纳的 SCHEMA 新增。
- **vendored 安装**：重新 clone 到临时目录、拷贝覆盖、提交。若有本地定制，先 diff `templates/SCHEMA.md`。
- **模式 C 拷贝**：重新下载替换。不知道某份拷贝是什么版本时，覆盖前先与仓库 diff——纯拷贝上的本地改动否则会被静默丢掉。
- **拷进项目的工具**不随 skill 升级——它们从此归你。拉新版工具时重新套用你的 CONFIG 块并重跑 `--selftest`。
- 你项目的 `wiki/` 内容**永不被升级触碰**——skill 发的是规则和模板，不是状态。

## 5. 排障

| 症状 | 原因 → 修法 |
|---|---|
| 新会话里 skill 没列出 | 路径不对（必须恰好是 home 或项目根下的 `.claude/skills/<名字>/skill.md`）→ `ls` 核对；或文件夹多嵌了一层（`.../wiki-management/cwiki/skill.md`）→ 把内容上移 |
| 列出了但从不触发 | 触发语在 skill.md frontmatter `description:` 里——先显式调用（"use the wiki-management skill"）确认它能工作，再核对你用的是列出的触发语 |
| 不同项目行为不一致 | 项目级拷贝（模式 B）遮蔽了用户全局的 → `ls <项目>/.claude/skills/` 看该项目解析到哪份 |
| `git pull` 报 "not a git repository" | 这份安装是纯拷贝（模式 C 或 vendored）→ 按 §4 重拷升级 |
| 协作者看到空的 skill 文件夹 | 嵌套 clone 被当 gitlink 提交了 → 二选一：vendor 或 submodule（§1 模式 B） |
| 工具装完一跑就 exit 1 | 这正是目的——它找到了违规。读证据行；brownfield 项目采纳期先 report-only 跑一周 |
| Windows 上 diff 全是换行噪声 | 仓库带 `.gitattributes`（LF）。2026-10 之前 vendor 的，重拷一份它 |

## 6. 卸载

删掉 skill 文件夹即可。你的 `wiki/` 和拷进 `scripts/maintenance/` 的工具独立于 skill，继续工作——skill 是方法论，wiki 是你的。
