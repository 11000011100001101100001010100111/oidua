  GNU nano 8.7.1                                                                                         oidua.py
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# --- [ UI Constants ] ---
RED = "\033[91m"
SILVER = "\033[37m"
RESET = "\033[0m"
LOG_FILE = Path("render_history.log")

ASCII_ART = f"""
{RED} █████╗ ███╗   ██╗███████╗██╗██████╗ ██╗     ███████╗
██╔══██╗████╗  ██║██╔════╝██║██╔══██╗██║     ██╔════╝
███████║██╔██╗ ██║███████╗██║██████╔╝██║     █████╗
██╔══██║██║╚██╗██║╚════██║██║██╔══██╗██║     ██╔══╝
██║  ██║██║ ╚████║███████║██║██████╔╝███████╗███████╗
╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝╚═════╝ ╚══════╝╚══════╝{RESET}
      {SILVER}>> ASSET TRANSCODER // VERSION 2026.03 <<{RESET}
"""

# --- [ Logic ] ---
def clean_exit():
    """Restores terminal state and executes a clean shutdown."""
    print(f"{RESET}", end="")
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{RED}┌─ SESSION TERMINATED {'─' * 38}┐{RESET}")
    print(f"{RED}│{RESET} TERMINAL ENVIRONMENT RESTORED.                       {RED}│{RESET}")
    print(f"{RED}└{'─' * 58}┘{RESET}\n")
    sys.exit(0)

def log_render(file_name, status="SUCCESS"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"  └── [{timestamp}] {file_name} :: {status}\n")

def draw_box(content, title="INFO"):
    width = 60
    print(f"{RED}┌─ {title} {'─' * (width - len(title) - 4)}┐{RESET}")
    for line in content:
        if len(line) > width - 4:
            line = line[:width-7] + "..."
        print(f"{RED}│{RESET} {line:<{width-2}} {RED}│{RESET}")
    print(f"{RED}└{'─' * (width - 2)}┘{RESET}")

def get_directory():
    current_dir = Path.cwd().resolve()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ASCII_ART)

        try:
            dirs = sorted([d for d in current_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
        except PermissionError:
            dirs = []

        lines = [
            f"LOC: {current_dir}",
            "",
            "[0] .. (UP ONE LEVEL)",
            f"{SILVER}[S] SELECT CURRENT DIRECTORY{RESET}",
            "[Q] QUIT TO TERMINAL",
            "--------------------------------------------------"
        ]

        for i, d in enumerate(dirs, 1):
            lines.append(f"[{i}] {d.name}/")

        draw_box(lines, "DIRECTORY NAVIGATOR")

        choice = input(f"{RED}NAVIGATE > {RESET}").strip().lower()

        if choice == 'q':
            return None
        elif choice == 's':
            return current_dir
        elif choice == '0':                                                                                                                                                                                                      current_dir = current_dir.parent
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(dirs):                                                                                                                                                                                                current_dir = dirs[idx-1]

def start_tui():
    while True:
        source_path = get_directory()
        if not source_path:
            break

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(ASCII_ART)

            assets = [f for f in source_path.glob("*.*") if f.suffix.lower() in ['.mp3', '.mp4', '.mov', '.mkv', '.wav']]

            if not assets:
                draw_box([f"DIR: {source_path.name}", "", "NO SUPPORTED MEDIA FOUND IN DIRECTORY.", "[B] BACK TO NAVIGATOR"], "WARNING")
                if input(f"{RED}ACTION > {RESET}").strip().lower() == 'b':
                    break
                continue

            lines = [f"DIR: {source_path.name}", ""]
            for i, a in enumerate(assets, 1):
                lines.append(f"[{i}] {a.name}")
            lines.append("")
            lines.append("[B] BACK TO NAVIGATOR")
            lines.append("[Q] QUIT SESSION")
            draw_box(lines, "BROWSER")

            choice = input(f"{RED}EXECUTE > {RESET}").strip().lower()
            if choice == 'q':
                return
            if choice == 'b':
                break
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(assets):
                continue

            target = assets[int(choice)-1]

            os.system('cls' if os.name == 'nt' else 'clear')
            print(ASCII_ART)
            draw_box([
                f"TARGET: {target.name}",
                "",
                "[1] AUDIO NORMALIZATION (MP3)",
                "[2] GIF HIGH-CONVERT (800px/15fps)",
                "[3] GIF LOW-CONVERT (480px/10fps/64-col)",
                "[B] BACK TO BROWSER"
            ], "ACTION MENU")

            action = input(f"{RED}SELECT ACTION > {RESET}").strip().lower()
            if action == 'b': continue

            out_name = input(f"{RED}OUTPUT NAME (no ext) > {RESET}").strip()
            if not out_name: continue

            out_dir = source_path / "renders"
            out_dir.mkdir(exist_ok=True)

            print(f"\n{RED}STATUS: PROCESSING...{RESET}")

            if action == '1':
                cmd = f'ffmpeg -hide_banner -loglevel error -y -i "{target}" -af loudnorm "{out_dir}/{out_name}.mp3"'
                if subprocess.run(cmd, shell=True).returncode == 0:
                    log_render(f"{out_name}.mp3")
                else:
                    log_render(f"{out_name}.mp3", "FAILED")
            elif action in ['2', '3']:
                vf = "fps=15,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" if action == '2' \
                     else "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3"
                cmd = f'ffmpeg -hide_banner -loglevel error -y -i "{target}" -vf "{vf}" "{out_dir}/{out_name}.gif"'
                if subprocess.run(cmd, shell=True).returncode == 0:
                    log_render(f"{out_name}.gif")
                else:
                    log_render(f"{out_name}.gif", "FAILED")

            input(f"\n{RED}COMPLETE. PRESS ENTER TO CONTINUE.{RESET}")

if __name__ == "__main__":
    try:
        start_tui()
