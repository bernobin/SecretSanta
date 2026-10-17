import json
import os
import shlex
import cmd

import httpx
import typer
import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()
BASE_URL = os.getenv("API_BASE_URL", "http://api:8000").rstrip("/")

app = typer.Typer(
    name="santa",
    help="Manage your Secret Santa sessions.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
users = typer.Typer(help="Create and inspect users.", no_args_is_help=True)
sessions = typer.Typer(help="Manage Secret Santa sessions.", no_args_is_help=True)

app.add_typer(users, name="users")
app.add_typer(sessions, name="sessions")


def request(method: str, path: str, **kwargs):
    try:
        response = httpx.request(
            method,
            f"{BASE_URL}{path}",
            timeout=15,
            **kwargs,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        console.print(
            Panel(
                Text(
                    f"HTTP {exc.response.status_code}\n"
                    f"{exc.response.text}",
                    style="red",
                ),
                title="[bold red]API Error[/]",
                border_style="red",
            )
        )
        return
    except httpx.HTTPError as exc:
        console.print(
            Panel(
                str(exc),
                title="[bold red]Connection Error[/]",
                subtitle=BASE_URL,
                border_style="red",
            )
        )
        return

    if response.status_code == 204 or not response.content:
        console.print("[bold green]✓[/] Success")
        return

    try:
        result = response.json()
    except ValueError:
        console.print(response.text)
        return

    console.print(
        Panel(
            Syntax(
                json.dumps(result, indent=2, ensure_ascii=False),
                "json",
                theme="monokai",
                word_wrap=True,
            ),
            title="[bold green]API Response[/]",
            border_style="green",
            expand=False,
        )
    )


@users.command("create")
def create_user(
    chatid: int = typer.Option(..., help="Telegram chat ID"),
    username: str | None = typer.Option(None, help="Telegram username"),
    first_name: str | None = typer.Option(None, help="First name"),
    last_name: str | None = typer.Option(None, help="Last name"),
):
    """Create a user."""
    request(
        "POST",
        "/users",
        json={
            "chatid": chatid,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        },
    )


@users.command("get")
def get_user(user_id: int):
    """Retrieve a user by internal user ID."""
    request("GET", f"/users/{user_id}")


@sessions.command("create")
def create_session(
    sessionname: str = typer.Option(..., help="Unique session name"),
    admin_userid: int = typer.Option(..., help="Admin's internal user ID"),
    seed: str | None = typer.Option(None, help="Optional draw seed"),
):
    """Create a Secret Santa session."""
    request(
        "POST",
        "/sessions",
        json={
            "sessionname": sessionname,
            "admin_userid": admin_userid,
            "seed": seed,
        },
    )


@sessions.command("status")
def get_status(sessionname: str):
    """Show session details and participants."""
    request("GET", f"/sessions/{sessionname}")


@sessions.command("signup")
def signup(sessionname: str, user_id: int):
    """Sign up a participant."""
    request("POST", f"/sessions/{sessionname}/participants/{user_id}")


@sessions.command("signoff")
def signoff(sessionname: str, user_id: int):
    """Remove a participant from a session."""
    request("DELETE", f"/sessions/{sessionname}/participants/{user_id}")


@sessions.command("start")
def start_session(sessionname: str):
    """Start the draw and return anonymized matchings."""
    request("POST", f"/sessions/{sessionname}/start")


@sessions.command("end")
def end_session(sessionname: str):
    """End the session and reveal all matchings."""
    if typer.confirm(
        f"End session '{sessionname}' and reveal its matchings?",
        default=False,
    ):
        request("POST", f"/sessions/{sessionname}/end")
    else:
        console.print("[yellow]Cancelled.[/]")


class SantaShell(cmd.Cmd):
    prompt = "\033[1;35msanta ❯ \033[0m"
    intro = ""

    def emptyline(self):
        pass

    def default(self, line: str):
        """Dispatch each entered command through Typer."""
        try:
            args = shlex.split(line)
            if not args:
                return

            if args[0] == "api":
                console.print(f"[bold cyan]API:[/] {BASE_URL}")
                return

            if args[0] == "clear":
                console.clear()
                return

            if args[0] in ("quit", "exit"):
                return self.do_quit("")

            app(args=args, standalone_mode=False)

        except (typer.Exit, click.exceptions.Exit):
            pass
        except click.exceptions.ClickException as exc:
            exc.show()
        except SystemExit:
            pass
        except ValueError as exc:
            console.print(f"[red]Invalid input:[/] {exc}")

    def do_help(self, arg: str):
        """Show help: help, help users, or help sessions."""
        args = shlex.split(arg)

        if args:
            self.default(" ".join(shlex.quote(a) for a in args) + " --help")
            return

        table = Table(
            title="Available Commands",
            border_style="magenta",
            header_style="bold cyan",
        )
        table.add_column("Command", style="bold green")
        table.add_column("Description")

        table.add_row("users --help", "User management commands")
        table.add_row("sessions --help", "Session management commands")
        table.add_row("api", "Show the configured API URL")
        table.add_row("clear", "Clear the terminal")
        table.add_row("quit / exit", "Exit the interactive shell")

        console.print(table)
        console.print(
            "\n[dim]Tip: use [bold]help users[/bold] or "
            "[bold]help sessions[/bold] for command details.[/dim]"
        )

    def do_quit(self, arg: str):
        """Exit the interactive shell."""
        console.print("[dim]Goodbye! 🎅[/dim]")
        return True


def main():
    console.print(
        Panel(
            "[bold red]🎅 Secret Santa CLI[/]\n"
            "[white]Manage users, organize sessions, and run your draw.[/]\n\n"
            f"[bold cyan]API[/]  {BASE_URL}\n"
            "[dim]Type help to get started, or quit to exit.[/]",
            border_style="red",
            padding=(1, 3),
        )
    )
    SantaShell().cmdloop()


if __name__ == "__main__":
    main()
