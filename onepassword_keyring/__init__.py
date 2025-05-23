import shutil
import subprocess
import sys
import shlex

from keyring import backend
from jaraco.classes import properties
from keyring.errors import PasswordDeleteError

PRIORITY = 10


def cli_exec(command: str):
    result = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout, result.stderr


def _user_is_authenticated():
    command = "op whoami"
    stdout, stderr = cli_exec(command)
    if stderr:
        return False
    return True


def sign_in(account: str | None = None):
    """
    Sign in to 1Password.

    If an account is provided, sign in to that account. Otherwise, sign in to the default account. 
    Accounts are identified by URL (e.g. my.1password.com) or the account's 26-digit alphanumeric UUID.
    """
    command = "op signin"
    if account:
        command += f" --account {account}"
    stdout, stderr = cli_exec(command)
    if stderr:
        raise RuntimeError("Failed to sign in to 1Password: " + stderr)
    return True

def _auth():
    if not _user_is_authenticated():
        sign_in()
    return True

def _item_exists(service, username):
    command = f'op item get "{service}" --fields username'
    stdout, stderr = cli_exec(command)
    if stderr:
        if "Specify the item with its UUID, name, or domain." in stderr:
            return False
        raise RuntimeError("Error checking if item exists: " + stderr)
    else:
        return stdout.strip() == username


def _onepassword_cli_installed():
    return bool(shutil.which("op"))


class OnePasswordBackend(backend.KeyringBackend):

    @properties.classproperty
    @classmethod
    def priority(cls):
        if not _onepassword_cli_installed():
            raise RuntimeError(
                "Requires onepassword cli: https://developer.1password.com/docs/cli/get-started/"
            )

        return PRIORITY

    def get_password(self, service, username):
        _auth()
        command = f'op item get "{service}" --fields username,password --reveal'
        stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to get password: " + stderr)
        else:
            fetched_username, password = stdout.strip().split(",")
            if username != fetched_username:
                raise RuntimeError(f"Username mismatch: Provided username was {username}, expected username was {fetched_username}")
            return password.strip()

    def set_password(self, service, username, password):
        _auth()
        if _item_exists(service, username):
            command = f'op item edit "{service}" username="{username}" password="{password}"'
            stdout, stderr = cli_exec(command)
        else:
            command = f'op item create title="{service}" username="{username}" password="{password}" --category=login'
            stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to set password: " + stderr)

    def delete_password(self, service, username):
        _auth()
        if _item_exists(service, username):
            command = f'op item delete "{service}"'
            stdout, stderr = cli_exec(command)
            if stderr:
                raise RuntimeError("Failed to delete password: " + stderr)
        else:
            e = sys.exc_info()[0]
            raise PasswordDeleteError(e)

    def get_otp(self, service, username):
        _auth()
        command = f'op item get "{service}" --otp --reveal'
        stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to get otp: " + stderr)
        else:
            return stdout.strip()

    def get_item(self, service):
        _auth()
        command = f'op item get "{service}" --reveal'
        stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to get item: " + stderr)
        return stdout.strip()

    def get_credential(self, service, username=None):
        """
        Return a credential object stored in the active keyring. Unlike the calling keyring.get_credential, this method ignores the username argument.
        """
        _auth()
        command = f'op item get "{service}" --reveal'
        stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to get item: " + stderr)
        return stdout.strip()
