#!/bin/bash
# common.sh — 公共函数库，供各 hook 文件 source
# 注意：不加 set -euo pipefail，避免 source 时覆盖调用方的 shell options

# project_root — 稳定解析项目根目录
# 优先使用 Claude Code 注入的 CLAUDE_PROJECT_DIR；其次使用 git root；最后退回当前目录。
# 输出绝对路径，避免 hook 从嵌套 cwd 执行时误读/误写。
project_root() {
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "$CLAUDE_PROJECT_DIR" ]; then
    (cd "$CLAUDE_PROJECT_DIR" 2>/dev/null && pwd -P) && return
  fi
  local git_root
  git_root=$(git rev-parse --show-toplevel 2>/dev/null || true)
  if [ -n "$git_root" ] && [ -d "$git_root" ]; then
    (cd "$git_root" 2>/dev/null && pwd -P) && return
  fi
  pwd -P
}

# resolve_project_path <path> — 将相对路径按项目根目录解析为绝对路径。
resolve_project_path() {
  local path="$1"
  case "$path" in
    /*) printf '%s\n' "$path" ;;
    *) printf '%s/%s\n' "$(project_root)" "$path" ;;
  esac
}

# discover_active_book — 单本书查询（活跃书目）
# 优先 root/.active-book；其次 find 第一个 追踪/ (长篇) 或 正文/ / 正文.md (短篇) 目录。
# 使用场景：session-start / session-end / pre-compact / post-compact —— 一次会话只关心当前活跃的那本书。
# 支持任意嵌套深度（maxdepth 6 覆盖 书本/{日期}/{书名}/ 等分组结构）。
discover_active_book() {
  local root
  root=$(project_root)

  if [ -f "$root/.active-book" ]; then
    local active
    active=$(sed -n '1p' "$root/.active-book" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || true)
    if [ -n "$active" ]; then
      resolve_project_path "$active"
      return
    fi
  fi

  # 长篇优先（追踪/ 目录存在）
  local first
  first=$(find "$root" -maxdepth 6 -type d -name "追踪" -print -quit 2>/dev/null || true)
  if [ -n "$first" ]; then
    dirname "$first"
    return
  fi

  # 短篇 fallback：查找 正文/ 目录或 正文.md
  local story_path
  story_path=$(find "$root" -maxdepth 6 \( -type d -name "正文" -o -type f -name "正文.md" \) -print -quit 2>/dev/null || true)
  if [ -n "$story_path" ]; then
    dirname "$story_path"
  fi
}

# discover_all_books — 多本书查询（项目内所有书目）
# 输出：换行分隔的绝对目录路径列表（不含重复）。
# 使用场景：detect-story-gaps —— 需要遍历项目内所有书目做缺口检测。
# 不假设书在固定前缀下，只要目录下包含 追踪/ 或 正文/ 或 正文.md 就算一本书。
discover_all_books() {
  local root
  root=$(project_root)
  # 用 awk 去重保持插入顺序（bash 3.2 兼容，不用关联数组）
  {
    # 追踪/ 父目录（长篇/中篇，任意深度）
    find "$root" -maxdepth 6 -type d -name "追踪" -print 2>/dev/null | while IFS= read -r d; do dirname "$d"; done
    # 正文/ 父目录 或 正文.md 父目录（短篇，任意深度）
    find "$root" -maxdepth 6 \( -type d -name "正文" -o -type f -name "正文.md" \) -print 2>/dev/null | while IFS= read -r d; do dirname "$d"; done
  } | awk 'NF && !seen[$0]++'
}

# 旧名 alias，仅供外部自定义 hook 引用；新代码用 discover_active_book / discover_all_books。
discover_book_dir() {
  discover_active_book "$@"
}
