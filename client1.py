import asyncio
import os
import re
import threading
import webbrowser
import tempfile
from datetime import datetime
from urllib.request import urlretrieve
from urllib.error import URLError
from urllib.parse import quote
import shutil

import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog, messagebox

import websockets
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ── Server config ──
SERVER_HOST = "localhost"
SERVER_PORT = 8000
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Local output directory (same machine as server)
LOCAL_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# ── Color palette ──
BG_DARK = "#1e1e2e"       # main background
SIDEBAR_BG = "#181825"     # sidebar / header
ACCENT = "#89b4fa"         # accent blue
ACCENT_DARK = "#74c7ec"    # hover blue
USER_BUBBLE = "#313244"    # user message bg
AI_BUBBLE = "#45475a"      # AI message bg
TEXT_PRIMARY = "#cdd6f4"   # main text
TEXT_SECONDARY = "#a6adc8" # muted text
TEXT_BRIGHT = "#ffffff"     # bright text
ONLINE_GREEN = "#a6e3a1"   # online dot
OFFLINE_RED = "#f38ba8"    # offline dot
INPUT_BG = "#313244"       # input field bg
BORDER_COLOR = "#45475a"   # subtle borders
SEND_BG = "#89b4fa"        # send button
SEND_HOVER = "#74c7ec"     # send button hover


class ChatApp:
    def __init__(self, root: tb.Window):
        self.root = root
        self.root.title("EduAttend AI — Chat Assistant")
        self.root.geometry("750x600")
        self.root.minsize(500, 400)
        self.root.configure(bg=BG_DARK)

        # ── Custom fonts ──
        self.font_heading = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.font_body = tkfont.Font(family="Segoe UI", size=10)
        self.font_small = tkfont.Font(family="Segoe UI", size=9)
        self.font_input = tkfont.Font(family="Segoe UI", size=11)
        self.font_sender = tkfont.Font(family="Segoe UI", size=9, weight="bold")

        self._build_header()
        self._build_status_bar()
        self._build_input_area()
        self._build_chat_area()

        self.client_id = "User1"
        self.websocket = None

        # Async loop in background thread
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    # ────────────────────────────────────────
    # UI BUILDING
    # ────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=SIDEBAR_BG, height=56)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        # Icon circle
        icon_canvas = tk.Canvas(header, width=36, height=36, bg=SIDEBAR_BG, highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(16, 10), pady=10)
        icon_canvas.create_oval(2, 2, 34, 34, fill=ACCENT, outline="")
        icon_canvas.create_text(18, 18, text="AI", font=("Segoe UI", 11, "bold"), fill=BG_DARK)

        # Title + subtitle
        title_frame = tk.Frame(header, bg=SIDEBAR_BG)
        title_frame.pack(side=tk.LEFT, fill=tk.Y, pady=8)

        tk.Label(
            title_frame, text="EduAttend AI", font=self.font_heading,
            bg=SIDEBAR_BG, fg=TEXT_BRIGHT, anchor=tk.W
        ).pack(anchor=tk.W)
        tk.Label(
            title_frame, text="School Attendance Assistant", font=self.font_small,
            bg=SIDEBAR_BG, fg=TEXT_SECONDARY, anchor=tk.W
        ).pack(anchor=tk.W)

        # Connection indicator (right side)
        self.conn_frame = tk.Frame(header, bg=SIDEBAR_BG)
        self.conn_frame.pack(side=tk.RIGHT, padx=16)

        self.conn_dot = tk.Canvas(self.conn_frame, width=10, height=10, bg=SIDEBAR_BG, highlightthickness=0)
        self.conn_dot.pack(side=tk.LEFT, padx=(0, 6))
        self.conn_dot_id = self.conn_dot.create_oval(1, 1, 9, 9, fill=OFFLINE_RED, outline="")

        self.conn_label = tk.Label(
            self.conn_frame, text="Connecting…", font=self.font_small,
            bg=SIDEBAR_BG, fg=TEXT_SECONDARY
        )
        self.conn_label.pack(side=tk.LEFT)

    def _build_chat_area(self):
        container = tk.Frame(self.root, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Text widget acts as the chat canvas
        self.chat_area = tk.Text(
            container,
            wrap=tk.WORD,
            state="disabled",
            bg=BG_DARK,
            fg=TEXT_PRIMARY,
            font=self.font_body,
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=14,
            cursor="arrow",
            spacing1=2,
            spacing3=2,
        )
        # Scrollbar
        scrollbar = tb.Scrollbar(container, orient=tk.VERTICAL, command=self.chat_area.yview, bootstyle="round")
        self.chat_area.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── Text Tags for styling ──
        self.chat_area.tag_configure("user_name", foreground=ACCENT, font=self.font_sender)
        self.chat_area.tag_configure("ai_name", foreground=ONLINE_GREEN, font=self.font_sender)
        self.chat_area.tag_configure("user_msg", foreground=TEXT_BRIGHT, font=self.font_body,
                                     background=USER_BUBBLE, lmargin1=60, lmargin2=60,
                                     rmargin=20, spacing1=2, spacing3=6,
                                     relief="flat", borderwidth=0)
        self.chat_area.tag_configure("ai_msg", foreground=TEXT_PRIMARY, font=self.font_body,
                                     background=AI_BUBBLE, lmargin1=20, lmargin2=20,
                                     rmargin=60, spacing1=2, spacing3=6,
                                     relief="flat", borderwidth=0)
        self.chat_area.tag_configure("timestamp", foreground=TEXT_SECONDARY, font=self.font_small,
                                     justify=tk.CENTER)
        self.chat_area.tag_configure("system", foreground=TEXT_SECONDARY, font=self.font_small,
                                     justify=tk.CENTER, spacing1=6, spacing3=6)
        self.chat_area.tag_configure("spacer", font=tkfont.Font(size=4))

        # ── Markdown rendering tags ──
        self.font_bold = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.font_italic = tkfont.Font(family="Segoe UI", size=10, slant="italic")
        self.font_bold_italic = tkfont.Font(family="Segoe UI", size=10, weight="bold", slant="italic")
        self.font_code_inline = tkfont.Font(family="Consolas", size=10)
        self.font_code_block = tkfont.Font(family="Consolas", size=9)
        self.font_h1 = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_h2 = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.font_h3 = tkfont.Font(family="Segoe UI", size=11, weight="bold")

        self.chat_area.tag_configure("md_bold", font=self.font_bold)
        self.chat_area.tag_configure("md_italic", font=self.font_italic)
        self.chat_area.tag_configure("md_bold_italic", font=self.font_bold_italic)
        self.chat_area.tag_configure("md_code", font=self.font_code_inline,
                                     background="#585b70", foreground="#f5c2e7")
        self.chat_area.tag_configure("md_codeblock", font=self.font_code_block,
                                     background="#181825", foreground="#a6e3a1",
                                     lmargin1=40, lmargin2=40, rmargin=40,
                                     spacing1=4, spacing3=4)
        self.chat_area.tag_configure("md_h1", font=self.font_h1, foreground=TEXT_BRIGHT,
                                     spacing1=6, spacing3=4)
        self.chat_area.tag_configure("md_h2", font=self.font_h2, foreground=TEXT_BRIGHT,
                                     spacing1=4, spacing3=3)
        self.chat_area.tag_configure("md_h3", font=self.font_h3, foreground=TEXT_BRIGHT,
                                     spacing1=3, spacing3=2)
        self.chat_area.tag_configure("md_bullet", lmargin1=40, lmargin2=55)
        self.chat_area.tag_configure("md_hr", foreground=BORDER_COLOR, justify=tk.CENTER,
                                     spacing1=6, spacing3=6)

        # ── Table tags ──
        self.font_table = tkfont.Font(family="Consolas", size=10)
        self.font_table_header = tkfont.Font(family="Consolas", size=10, weight="bold")
        self.chat_area.tag_configure("md_table_header", font=self.font_table_header,
                                     foreground=TEXT_BRIGHT, background="#313244",
                                     lmargin1=20, lmargin2=20, rmargin=20,
                                     spacing1=2, spacing3=0)
        self.chat_area.tag_configure("md_table_row", font=self.font_table,
                                     foreground=TEXT_PRIMARY, background=AI_BUBBLE,
                                     lmargin1=20, lmargin2=20, rmargin=20,
                                     spacing1=0, spacing3=0)
        self.chat_area.tag_configure("md_table_row_alt", font=self.font_table,
                                     foreground=TEXT_PRIMARY, background="#3b3d52",
                                     lmargin1=20, lmargin2=20, rmargin=20,
                                     spacing1=0, spacing3=0)
        self.chat_area.tag_configure("md_table_border", font=self.font_table,
                                     foreground=BORDER_COLOR,
                                     lmargin1=20, lmargin2=20, rmargin=20,
                                     spacing1=0, spacing3=0)

        # ── File download button tag ──
        self.font_download = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.chat_area.tag_configure("download_btn",
                                     font=self.font_download,
                                     foreground=BG_DARK,
                                     background=ONLINE_GREEN,
                                     spacing1=6, spacing3=6,
                                     lmargin1=20, lmargin2=20)
        self.chat_area.tag_configure("download_btn_hover",
                                     font=self.font_download,
                                     foreground=BG_DARK,
                                     background="#94e2d5",
                                     spacing1=6, spacing3=6,
                                     lmargin1=20, lmargin2=20)
        self._download_links = {}  # tag_name -> filename

    def _build_input_area(self):
        # Separator line
        tk.Frame(self.root, bg=BORDER_COLOR, height=1).pack(fill=tk.X)

        input_bar = tk.Frame(self.root, bg=SIDEBAR_BG)
        input_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Inner padding frame
        inner = tk.Frame(input_bar, bg=SIDEBAR_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

        # Entry container with rounded look
        entry_container = tk.Frame(inner, bg=INPUT_BG, highlightbackground=BORDER_COLOR,
                                   highlightthickness=1)
        entry_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.message_entry = tk.Entry(
            entry_container,
            bg=INPUT_BG,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            font=self.font_input,
            relief="flat",
            borderwidth=0,
        )
        self.message_entry.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.message_entry.bind("<Return>", self.send_message)

        # Placeholder
        self._placeholder_active = True
        self.message_entry.insert(0, "Type a message…")
        self.message_entry.config(fg=TEXT_SECONDARY)
        self.message_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.message_entry.bind("<FocusOut>", self._on_entry_focus_out)

        # Send button
        self.send_btn = tk.Button(
            inner, text="  ➤  Send  ",
            bg=SEND_BG, fg=BG_DARK,
            activebackground=SEND_HOVER, activeforeground=BG_DARK,
            font=("Segoe UI", 12, "bold"),
            relief="flat", cursor="hand2",
            borderwidth=0, padx=20, pady=8,
            command=self.send_message,
        )
        self.send_btn.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg="#11111b", height=24)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            self.status_bar, text="Waiting for connection…",
            bg="#11111b", fg=TEXT_SECONDARY, font=self.font_small,
            anchor=tk.W, padx=12,
        )
        self.status_label.pack(fill=tk.X)

    # ────────────────────────────────────────
    # PLACEHOLDER LOGIC
    # ────────────────────────────────────────
    def _on_entry_focus_in(self, event=None):
        if self._placeholder_active:
            self.message_entry.delete(0, tk.END)
            self.message_entry.config(fg=TEXT_PRIMARY)
            self._placeholder_active = False

    def _on_entry_focus_out(self, event=None):
        if not self.message_entry.get().strip():
            self._placeholder_active = True
            self.message_entry.insert(0, "Type a message…")
            self.message_entry.config(fg=TEXT_SECONDARY)

    # ────────────────────────────────────────
    # STATUS / DISPLAY
    # ────────────────────────────────────────
    def update_status(self, status: str, connected: bool = False):
        self.status_label.config(text=status)
        color = ONLINE_GREEN if connected else OFFLINE_RED
        self.conn_dot.itemconfig(self.conn_dot_id, fill=color)
        self.conn_label.config(text="Online" if connected else "Offline")

    def display_message(self, message: str, is_sent: bool = False):
        self.chat_area.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M")

        if is_sent:
            self.chat_area.insert(tk.END, f"  You  •  {timestamp}\n", "user_name")
            self.chat_area.insert(tk.END, f" {message} \n", "user_msg")
        else:
            self.chat_area.insert(tk.END, f"  AI Assistant  •  {timestamp}\n", "ai_name")
            self._render_markdown(message)
            # Check for downloadable file references in the message
            self._detect_and_insert_download(message)

        # Small spacer between messages
        self.chat_area.insert(tk.END, "\n", "spacer")

        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

    def _render_markdown(self, text: str):
        """Parse markdown in text and insert with styled tags into chat_area."""
        lines = text.split("\n")
        in_code_block = False
        code_block_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # ── Code block fence ──
            if line.strip().startswith("```"):
                if in_code_block:
                    code_text = "\n".join(code_block_lines)
                    self.chat_area.insert(tk.END, f" {code_text} \n", ("md_codeblock",))
                    code_block_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                i += 1
                continue

            if in_code_block:
                code_block_lines.append(line)
                i += 1
                continue

            # ── Table detection ──
            if "|" in line and i + 1 < len(lines):
                table_lines = self._collect_table(lines, i)
                if table_lines:
                    self._render_table(table_lines)
                    i += len(table_lines)
                    continue

            # ── Horizontal rule ──
            if re.match(r"^\s*[-*_]{3,}\s*$", line):
                self.chat_area.insert(tk.END, "━" * 40 + "\n", ("md_hr",))
                i += 1
                continue

            # ── Headers ──
            h_match = re.match(r"^(#{1,3})\s+(.*)", line)
            if h_match:
                level = len(h_match.group(1))
                header_text = h_match.group(2)
                tag = f"md_h{level}"
                self.chat_area.insert(tk.END, f" {header_text}\n", (tag, "ai_msg"))
                i += 1
                continue

            # ── Bullet / numbered list ──
            list_match = re.match(r"^(\s*)([-*+•]|\d+\.)\s+(.*)", line)
            if list_match:
                marker = list_match.group(2)
                content = list_match.group(3)
                bullet = "  •  " if not marker[0].isdigit() else f"  {marker} "
                self._insert_inline_md(f"{bullet}{content}\n", ("ai_msg", "md_bullet"))
                i += 1
                continue

            # ── Normal paragraph line ──
            if line.strip():
                self._insert_inline_md(f" {line} \n", ("ai_msg",))
            else:
                self.chat_area.insert(tk.END, "\n", ("ai_msg",))

            i += 1

        # Handle unclosed code block
        if in_code_block and code_block_lines:
            code_text = "\n".join(code_block_lines)
            self.chat_area.insert(tk.END, f" {code_text} \n", ("md_codeblock",))

    def _collect_table(self, lines: list, start: int) -> list:
        """Collect consecutive lines that form a markdown table starting at index."""
        table = []
        for j in range(start, len(lines)):
            line = lines[j].strip()
            if "|" in line:
                table.append(line)
            else:
                break
        # Valid table needs at least header + separator + 1 row = 3 lines
        # But also accept header + separator = 2 lines
        if len(table) >= 2:
            # Check if second line is a separator (e.g. |---|---| or --- | ---)
            sep = table[1]
            if re.match(r"^[\s|:-]+$", sep.replace("-", "")):
                # It's likely a separator... but let's be more lenient
                pass
            cleaned = sep.replace("|", "").replace("-", "").replace(":", "").strip()
            if cleaned == "":
                return table
        return []

    def _render_table(self, table_lines: list):
        """Render a markdown table with aligned columns into the chat_area."""
        # Parse all rows into cells
        rows = []
        for line in table_lines:
            line = line.strip()
            if line.startswith("|"):
                line = line[1:]
            if line.endswith("|"):
                line = line[:-1]
            cells = [c.strip() for c in line.split("|")]
            rows.append(cells)

        if len(rows) < 2:
            return

        header = rows[0]
        # Skip separator row (index 1)
        data_rows = rows[2:] if len(rows) > 2 else []

        # Calculate column widths
        num_cols = len(header)
        col_widths = [len(h) for h in header]
        for row in data_rows:
            for ci in range(min(len(row), num_cols)):
                col_widths[ci] = max(col_widths[ci], len(row[ci]))
        # Minimum width and add padding
        col_widths = [max(w, 4) + 2 for w in col_widths]

        def format_row(cells, widths):
            parts = []
            for ci in range(len(widths)):
                val = cells[ci] if ci < len(cells) else ""
                parts.append(f" {val:<{widths[ci] - 1}}")
            return "│" + "│".join(parts) + "│"

        def border_line(widths, top=False, bottom=False):
            if top:
                parts = ["─" * w for w in widths]
                return "┌" + "┬".join(parts) + "┐"
            elif bottom:
                parts = ["─" * w for w in widths]
                return "└" + "┴".join(parts) + "┘"
            else:
                parts = ["─" * w for w in widths]
                return "├" + "┼".join(parts) + "┤"

        # Insert top border
        self.chat_area.insert(tk.END, border_line(col_widths, top=True) + "\n", ("md_table_border",))
        # Insert header
        self.chat_area.insert(tk.END, format_row(header, col_widths) + "\n", ("md_table_header",))
        # Insert separator
        self.chat_area.insert(tk.END, border_line(col_widths) + "\n", ("md_table_border",))
        # Insert data rows with alternating colors
        for ri, row in enumerate(data_rows):
            tag = "md_table_row_alt" if ri % 2 == 1 else "md_table_row"
            self.chat_area.insert(tk.END, format_row(row, col_widths) + "\n", (tag,))
        # Insert bottom border
        self.chat_area.insert(tk.END, border_line(col_widths, bottom=True) + "\n", ("md_table_border",))

    def _insert_inline_md(self, text: str, base_tags: tuple):
        """Parse inline markdown (bold, italic, code) and insert with tags."""
        # Pattern order matters: bold+italic first, then bold, italic, inline code
        pattern = re.compile(
            r"(\*\*\*(.+?)\*\*\*"   # ***bold italic***
            r"|\*\*(.+?)\*\*"       # **bold**
            r"|\*(.+?)\*"           # *italic*
            r"|`(.+?)`"             # `inline code`
            r")"
        )
        last_end = 0
        for m in pattern.finditer(text):
            # Insert text before this match
            if m.start() > last_end:
                self.chat_area.insert(tk.END, text[last_end:m.start()], base_tags)

            if m.group(2):  # bold italic
                self.chat_area.insert(tk.END, m.group(2), base_tags + ("md_bold_italic",))
            elif m.group(3):  # bold
                self.chat_area.insert(tk.END, m.group(3), base_tags + ("md_bold",))
            elif m.group(4):  # italic
                self.chat_area.insert(tk.END, m.group(4), base_tags + ("md_italic",))
            elif m.group(5):  # inline code
                self.chat_area.insert(tk.END, f" {m.group(5)} ", base_tags + ("md_code",))

            last_end = m.end()

        # Remaining text after last match
        if last_end < len(text):
            self.chat_area.insert(tk.END, text[last_end:], base_tags)

    def display_system_message(self, message: str):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"— {message} —\n", "system")
        self.chat_area.insert(tk.END, "\n", "spacer")
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

    # ────────────────────────────────────────
    # PDF DOWNLOAD
    # ────────────────────────────────────────
    def _detect_and_insert_download(self, message: str):
        """Scan message for file paths (.pdf) and insert a download button."""
        # Match common patterns: full paths or just filenames
        # e.g. output/surat_peringatan_xxx.pdf  or  C:\...\output\xxx.pdf
        patterns = [
            r'([\w/\\:.-]+\.pdf)',  # any path ending in .pdf
        ]
        filenames_found = set()
        for pat in patterns:
            for match in re.finditer(pat, message, re.IGNORECASE):
                raw = match.group(1)
                # Extract just the filename (last part of path)
                fname = os.path.basename(raw.replace("\\\\", "/").replace("\\", "/"))
                if fname and fname not in filenames_found:
                    filenames_found.add(fname)

        if not filenames_found:
            return

        for fname in filenames_found:
            self._insert_download_button(fname)

    def _insert_download_button(self, filename: str):
        """Insert a clickable download button into the chat area."""
        tag_id = f"dl_{len(self._download_links)}_{filename}"
        self._download_links[tag_id] = filename

        # Create unique tags for this button
        self.chat_area.tag_configure(tag_id, font=self.font_download,
                                     foreground=BG_DARK, background=ONLINE_GREEN,
                                     spacing1=4, spacing3=4,
                                     lmargin1=20, lmargin2=20)

        btn_text = f"  📄  Download: {filename}  "
        self.chat_area.insert(tk.END, f"{btn_text}\n", (tag_id,))
        self.chat_area.insert(tk.END, "\n", "spacer")

        # Bind click + hover events to this tag
        self.chat_area.tag_bind(tag_id, "<Button-1>",
                                lambda e, fn=filename: self._download_file(fn))
        self.chat_area.tag_bind(tag_id, "<Enter>",
                                lambda e, t=tag_id: self._on_download_hover(t, True))
        self.chat_area.tag_bind(tag_id, "<Leave>",
                                lambda e, t=tag_id: self._on_download_hover(t, False))
        # Change cursor on hover
        self.chat_area.tag_configure(tag_id, underline=False)

    def _on_download_hover(self, tag_id: str, entering: bool):
        """Change button appearance on hover."""
        if entering:
            self.chat_area.tag_configure(tag_id, background="#94e2d5")
            self.chat_area.config(cursor="hand2")
        else:
            self.chat_area.tag_configure(tag_id, background=ONLINE_GREEN)
            self.chat_area.config(cursor="arrow")

    def _download_file(self, filename: str):
        """Download file from server, or copy from local output dir as fallback."""
        # Ask user where to save
        save_path = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
            title="Save PDF File",
        )
        if not save_path:
            return  # user cancelled

        # ── Strategy 1: Try local copy first (faster, no server needed) ──
        local_path = os.path.join(LOCAL_OUTPUT_DIR, filename)
        if os.path.exists(local_path):
            try:
                shutil.copy2(local_path, save_path)
                self.display_system_message(f"File saved: {os.path.basename(save_path)}")
                if messagebox.askyesno("File Saved", f"File saved to:\n{save_path}\n\nOpen now?"):
                    os.startfile(save_path)
                return
            except Exception:
                pass  # fall through to server download

        # ── Strategy 2: Download from server with URL-encoded filename ──
        encoded_name = quote(filename, safe="")
        url = f"{BASE_URL}/download/{encoded_name}"

        try:
            urlretrieve(url, save_path)
            self.display_system_message(f"File saved: {os.path.basename(save_path)}")
            if messagebox.askyesno("File Downloaded", f"File saved to:\n{save_path}\n\nOpen now?"):
                os.startfile(save_path)
        except URLError as e:
            messagebox.showerror(
                "Download Error",
                f"Could not download file.\n\n"
                f"Filename: {filename}\n"
                f"URL: {url}\n"
                f"Local path: {local_path}\n\n"
                f"Error: {e}\n\n"
                f"Make sure the API server (api.py) is running\n"
                f"and the file exists in the output/ folder."
            )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

    # ────────────────────────────────────────
    # SEND / RECEIVE
    # ────────────────────────────────────────
    def send_message(self, event=None):
        if self._placeholder_active:
            return
        message = self.message_entry.get().strip()
        if not message:
            return

        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.send(message), self.loop)
            self.display_message(message, is_sent=True)
            self.message_entry.delete(0, tk.END)
        else:
            self.display_system_message("Not connected yet. Please wait…")

    # ────────────────────────────────────────
    # WEBSOCKET
    # ────────────────────────────────────────
    def connect_to_server(self):
        try:
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.websocket_connection())
        except Exception as e:
            self.root.after(0, self.update_status, f"Connection error: {e}", False)
            self.root.after(0, self.display_system_message, f"Connection error: {e}")

    async def websocket_connection(self):
        uri = f"ws://{SERVER_HOST}:{SERVER_PORT}/ws/{self.client_id}"
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                self.root.after(0, self.update_status, "Connected to server", True)
                self.root.after(0, self.display_system_message, "Connected — You can start chatting")

                while True:
                    try:
                        message = await websocket.recv()
                        self.root.after(0, self.display_message, message, False)
                    except websockets.exceptions.ConnectionClosed:
                        self.root.after(0, self.update_status, "Server disconnected", False)
                        self.root.after(0, self.display_system_message, "Connection closed by server")
                        break
                    except Exception as e:
                        self.root.after(0, self.update_status, f"Error: {e}", False)
                        break
        except Exception as e:
            self.root.after(0, self.update_status, f"Cannot reach server", False)
            self.root.after(0, self.display_system_message, f"Could not connect: {e}")


if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = ChatApp(root)
    root.mainloop()
