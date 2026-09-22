#!/usr/bin/env python3
"""
lab_writeup.py — Cybersecurity Lab Writeup Template Generator
Generates a structured Markdown file with YAML frontmatter for lab writeups.
Supports HackTheBox, TryHackMe, and other platforms.
Works on Linux and macOS.
"""

import os
import re
from datetime import date

# ─── ANSI colour helpers (no extra deps needed) ────────────────────────────
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def banner():
    """Print a short ASCII banner."""
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════╗
║   🛡  Lab Writeup Template Generator    ║
╚══════════════════════════════════════════╝{RESET}
""")

# ─── INPUT HELPERS ──────────────────────────────────────────────────────────

def prompt(question: str, default: str = "") -> str:
    """Prompt the user for input, showing an optional default value."""
    hint = f" [{default}]" if default else ""
    answer = input(f"{YELLOW}{question}{hint}: {RESET}").strip()
    return answer if answer else default


def pick_from_list(label: str, options: list[str]) -> str:
    """Display a numbered list and return the user's choice."""
    print(f"\n{YELLOW}{label}{RESET}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt}")
    while True:
        raw = input(f"Choose [1-{len(options)}] or type your own: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        if raw:          # user typed a custom value
            return raw
        print("  Please enter a valid choice.")


# ─── FILENAME SANITISATION ─────────────────────────────────────────────────

def safe_filename(name: str) -> str:
    """
    Convert a lab name to a safe filename:
      • lowercase
      • spaces → underscores
      • strip characters that are unsafe on most filesystems
    """
    name = name.lower().strip()
    name = re.sub(r"[\s]+", "_", name)          # spaces to underscores
    name = re.sub(r"[^\w\-]", "", name)          # remove non-alphanumeric
    return name or "untitled_lab"


# ─── MARKDOWN TEMPLATE BUILDER ─────────────────────────────────────────────

def build_template(lab: str, date_str: str, platform: str, difficulty: str) -> str:
    """
    Return the full Markdown content with YAML frontmatter and all required
    sections in the specified order.
    """
    return f"""\
---
lab: "{lab}"
date: "{date_str}"
platform: "{platform}"
difficulty: "{difficulty}"
---

# Recon

---

# Enumeration

---

# Foothold Access

---

# Privilege Escalation

---

# Stuff I Learned

- Key takeaways
- New techniques
- Commands worth remembering
"""


# ─── FILE WRITING ───────────────────────────────────────────────────────────

def write_file(filename: str, content: str, output_dir: str) -> str:
    """
    Create the output directory if it doesn't exist, then write the file.
    Returns the full path of the created file.
    """
    os.makedirs(output_dir, exist_ok=True)   # create labs/ if missing
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


# ─── MAIN ───────────────────────────────────────────────────────────────────

def main():
    banner()

    # ── Collect user inputs ──────────────────────────────────────────────
    lab_name   = prompt("Lab name", "My Lab")
    date_str   = prompt("Date (YYYY-MM-DD)", str(date.today()))   # auto-fill today
    platform   = pick_from_list(
        "Platform:",
        ["HackTheBox", "TryHackMe", "PentesterLab", "VulnHub", "Proving Grounds", "Other"]
    )
    difficulty = pick_from_list(
        "Difficulty:",
        ["Easy", "Medium", "Hard", "Insane"]
    )

    # ── Build template & derive filename ─────────────────────────────────
    content   = build_template(lab_name, date_str, platform, difficulty)
    fname     = safe_filename(lab_name) + ".md"
    output_dir = "Labs"                         # save inside labs/ sub-folder

    # ── Write to disk ─────────────────────────────────────────────────────
    filepath = write_file(fname, content, output_dir)

    print(f"\n{GREEN}✔  Writeup template created:{RESET} {BOLD}{filepath}{RESET}\n")


if __name__ == "__main__":
    main()
