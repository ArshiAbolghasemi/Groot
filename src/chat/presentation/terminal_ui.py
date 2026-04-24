"""Terminal UI similar to Claude/Codex CLI."""

import logging
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class TerminalUI:
    """Clean terminal UI with conversation flow."""

    def __init__(self):
        self.console = Console()
        self.conversation_history: list[dict] = []
        self.current_answer_chunks: list[str] = []
        self.logs: list[str] = []
        self.max_logs = 5

    def print_header(self):
        """Print the header once at startup."""
        header = Text("Groot Chatbot", style="bold cyan", justify="center")
        self.console.print(Panel(header, style="bold blue"))
        self.console.print()

    def print_question(self, question: str):
        """Print user question."""
        self.console.print()
        self.console.print(f"[bold cyan]You:[/bold cyan] {question}")
        self.console.print()

    def start_answer(self):
        """Start printing the answer."""
        self.console.print("[bold green]Groot:[/bold green] ", end="")
        self.current_answer_chunks = []

    def append_answer_chunk(self, chunk: str):
        """Append a chunk to the current answer and print it."""
        self.current_answer_chunks.append(chunk)
        self.console.print(chunk, end="", markup=False)

    def finish_answer(self):
        """Finish the current answer."""
        self.console.print()  # New line after answer
        full_answer = "".join(self.current_answer_chunks)
        self.conversation_history.append({"role": "assistant", "content": full_answer})

    def print_blocked_message(self, message: str):
        """Print blocked/refusal message."""
        self.console.print()
        self.console.print(f"[bold yellow]Groot:[/bold yellow] {message}")
        self.console.print()

    def print_separator(self):
        """Print a subtle separator."""
        self.console.print("[dim]" + "─" * 80 + "[/dim]")

    def print_logs(self):
        """Print recent logs in a compact way."""
        if self.logs:
            self.console.print()
            self.console.print("[dim]Recent activity:[/dim]")
            for log in self.logs[-self.max_logs :]:
                self.console.print(f"[dim]{log}[/dim]")

    def add_log(self, message: str, level: str = "INFO"):
        """Add a log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_entry)
        if len(self.logs) > 20:
            self.logs = self.logs[-20:]

    def get_input(self) -> str:
        """Get input from user with a clean prompt."""
        self.console.print()
        return self.console.input("[bold cyan]You:[/bold cyan] ").strip()

    def print_error(self, error: str):
        """Print an error message."""
        self.console.print(f"[bold red]Error:[/bold red] {error}")

    def print_info(self, message: str):
        """Print an info message."""
        self.console.print(f"[dim]{message}[/dim]")

    def clear_screen(self):
        """Clear the screen."""
        self.console.clear()


class LogHandler(logging.Handler):
    """Custom log handler that sends logs to TerminalUI."""

    def __init__(self, ui: TerminalUI):
        super().__init__()
        self.ui = ui

    def emit(self, record: logging.LogRecord):
        """Emit a log record to the UI."""
        try:
            msg = self.format(record)
            # Extract just the message part
            if ": " in msg:
                msg = msg.split(": ", 1)[1]
            self.ui.add_log(msg, record.levelname)
        except Exception:
            self.handleError(record)
