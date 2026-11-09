#!/usr/bin/env python3
"""创建新需求文档骨架（多需求项目版，hi-dev-plus-skill 增强版）。

用法:
    python new_spec.py <slug> --title <需求标题> [--path <项目根目录>] [--priority P0]

行为:
1. 读取 <项目根目录>/docs/specs/INDEX.md 汇总索引，自动分配下一个需求编号
   REQ-{NNN}（索引不存在时从模板创建并从 001 开始）。
2. 在 <项目根目录>/docs/specs/req-{NNN}-{slug}/ 下依据 assets/templates/
   生成 8 个文档（含 07-test-report.md 测试报告），替换占位符，
   并创建 screenshots/ 测试截图目录。
3. 项目尚无 docs/specs/RESTRICTIONS.md 限制配置文件时，从模板创建
   （已存在时不覆盖，由项目维护者手工维护）。
4. 将新需求登记到 INDEX.md 需求清单，并更新状态统计。
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

TEMPLATES = [
    "README.md",
    "01-requirements.md",
    "02-high-level-design.md",
    "03-detailed-design.md",
    "04-tasks.md",
    "05-implementation.md",
    "06-acceptance.md",
    "07-test-report.md",
]

RESTRICTIONS_FILE = "RESTRICTIONS.md"

VALID_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ROW_RE = re.compile(r"^\|\s*REQ-(\d+)\s*\|")
SEP_ROW = re.compile(r"^\|(?:\s*:?-{2,}:?\s*\|)+\s*$")


def read_index(index_path: Path) -> tuple[int, str]:
    """返回 (下一个可用序号, 索引内容)。索引不存在时返回 (1, "")。"""
    if not index_path.exists():
        return 1, ""
    text = index_path.read_text(encoding="utf-8")
    seqs = [int(m.group(1)) for line in text.splitlines() if (m := ROW_RE.match(line))]
    return (max(seqs) + 1 if seqs else 1), text


def ensure_index(project_root: Path, skill_root: Path) -> str:
    """索引不存在时从模板创建，返回索引内容。"""
    index_path = project_root / "docs" / "specs" / "INDEX.md"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    template_path = skill_root / "assets" / "templates" / "INDEX.md"
    if not template_path.exists():
        return ""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    text = template_path.read_text(encoding="utf-8")
    index_path.write_text(text, encoding="utf-8", newline="\n")
    print(f"  创建 {index_path}")
    return text


def ensure_restrictions(project_root: Path, skill_root: Path) -> None:
    """项目级限制配置文件不存在时从模板创建；已存在时不覆盖。"""
    target = project_root / "docs" / "specs" / RESTRICTIONS_FILE
    if target.exists():
        print(f"  限制配置已存在（不覆盖）：{target}")
        return
    template_path = skill_root / "assets" / "templates" / RESTRICTIONS_FILE
    if not template_path.exists():
        print("  [警告] 未找到 RESTRICTIONS.md 模板，跳过限制配置创建")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    print(f"  创建限制配置：{target}")


def register_index(index_path: Path, text: str, seq: int, req_id: str,
                   title: str, priority: str, today: str) -> None:
    """在需求清单表登记新需求行（追加到表尾），并累加状态统计。"""
    new_row = f"| REQ-{seq:03d} | {req_id} | {title} | clarifying | 阶段 1 · 需求澄清 | {priority} | {today} | |"

    lines = [ln for ln in text.splitlines() if "（示例行" not in ln]
    # 统计现有数量
    m_ip = re.search(r"^\|\s*in-progress（进行中）\s*\|\s*(\d+)\s*\|", text, re.M)
    m_ac = re.search(r"^\|\s*accepted（已验收）\s*\|\s*(\d+)\s*\|", text, re.M)
    n_ip, n_ac = (int(m_ip.group(1)) if m_ip else 0), (int(m_ac.group(1)) if m_ac else 0)

    # 追加到需求清单表尾（最后一个 REQ 行之后；无则插入到首个分隔行后）
    req_row_idx = [i for i, ln in enumerate(lines) if ROW_RE.match(ln)]
    sep_idx = [i for i, ln in enumerate(lines) if SEP_ROW.match(ln)]
    if req_row_idx:
        lines.insert(req_row_idx[-1] + 1, new_row)
    elif sep_idx:
        lines.insert(sep_idx[0] + 1, new_row)
    else:
        print("[错误] INDEX.md 缺少需求清单表，无法登记（请核对模板结构）")
        sys.exit(1)

    # 更新状态统计行
    for i, ln in enumerate(lines):
        if re.match(r"^\|\s*in-progress（进行中）\s*\|\s*\d+\s*\|", ln):
            lines[i] = f"| in-progress（进行中） | {n_ip + 1} |"
        elif re.match(r"^\|\s*accepted（已验收）\s*\|\s*\d+\s*\|", ln):
            lines[i] = f"| accepted（已验收） | {n_ac} |"
        elif re.match(r"^\|\s*合计\s*\|\s*\d+\s*\|", ln):
            lines[i] = f"| 合计 | {n_ip + n_ac + 1} |"

    index_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"  登记汇总索引：REQ-{seq:03d} {title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="创建新需求文档骨架（自动编号并登记汇总索引）")
    parser.add_argument("slug", help="需求语义标识，短横线小写，如 middleware-info-module")
    parser.add_argument("--title", required=True, help="需求标题（用于 README 与汇总索引登记）")
    parser.add_argument("--path", default=".", help="项目根目录（默认当前目录）")
    parser.add_argument("--priority", default="P0", choices=["P0", "P1", "P2"], help="需求优先级")
    args = parser.parse_args()

    slug = args.slug
    if not VALID_SLUG.match(slug):
        print(f"[错误] slug 不合法: {slug}（要求：小写字母/数字/短横线）")
        return 1

    skill_root = Path(__file__).resolve().parent.parent
    template_dir = skill_root / "assets" / "templates"
    if not template_dir.is_dir():
        print(f"[错误] 未找到模板目录: {template_dir}")
        return 1

    project_root = Path(args.path).resolve()
    specs_dir = project_root / "docs" / "specs"
    index_path = specs_dir / "INDEX.md"

    seq, index_text = read_index(index_path)
    if not index_text:
        index_text = ensure_index(project_root, skill_root)
    if not index_text:
        print("[错误] 未找到 INDEX.md 模板")
        return 1

    req_id = f"req-{seq:03d}-{slug}"
    target_dir = specs_dir / req_id
    if target_dir.exists():
        print(f"[错误] 目录已存在: {target_dir}")
        return 1

    today = datetime.date.today().isoformat()
    title = args.title

    target_dir.mkdir(parents=True, exist_ok=True)
    for name in TEMPLATES:
        src = template_dir / name
        dst = target_dir / name
        text = src.read_text(encoding="utf-8")
        text = (
            text.replace("{requirement-id}", req_id)
            .replace("{req-no}", f"REQ-{seq:03d}")
            .replace("{需求标题}", title)
            .replace("{date}", today)
        )
        dst.write_text(text, encoding="utf-8", newline="\n")
        print(f"  创建 {dst}")

    # 测试截图存证目录
    screenshots_dir = target_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    print(f"  创建截图目录 {screenshots_dir}")

    # 项目级限制配置文件（不存在时创建，不覆盖）
    ensure_restrictions(project_root, skill_root)

    register_index(index_path, index_text, seq, req_id, title, args.priority, today)

    print(f"[完成] 需求 REQ-{seq:03d} 文档骨架已建立: {target_dir}")
    print("下一步：阅读 docs/specs/RESTRICTIONS.md 限制条款，进入阶段 1（需求澄清），填写 01-requirements.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
