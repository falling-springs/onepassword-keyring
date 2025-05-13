# OnePassword Keyring

Implementation of the [Keyring](https://pypi.org/project/keyring/) backend code reading secrets from [1Password](https://1password.com) using [1password-cli](https://developer.1password.com/docs/cli/get-started/).

## Overview

The [Keyring](https://pypi.org/project/keyring/) python package provides a handy single point of entry for any secret holding system.

This projects allows Keyring to read secrets from 1Password, a multiplatform cloud password manager. It is based on and forked from [bitwarden-keyring](https://github.com/ewjoachim/bitwarden-keyring) by [ewjoachim](https://github.com/ewjoachim).

This backend assumes that it will be used in the context of a CLI application, and that it can communicate with the user using `sdtin`, `stdout` and `stderr`.

## Requirements

This project uses the official [1Password CLI](https://developer.1password.com/docs/cli/get-started/). You will need to install it and configure it before using this backend.

## Installation and configuration

```
pip install onepassword-keyring
```

## Usage

Use as a normal keyring backend. It is installed with priority 10 so it's likely going to be selected
first.

`onepassword-keyring` will automatically ask for credentials when needed.

### Example
```
import keyring
from onepassword_keyring import OnePasswordBackend

# Set 1Password as your keyring
keyring.set_keyring(OnePasswordBackend())

# If you have more than one 1Password account, either sign in manually...:
from onepassword_keyring import sign_in
sign_in(account="my.1password.com")

# ...Or set the OP_ACCOUNT environment variable
import os
os.environ["OP_ACCOUNT"] = "my.1password.com"

# Create a new item
kr.set_password("my-password-item", "my-username", "my-password")

# Look up your password
my_password = kr.get_password("my-password-item", "my-username")
print(my_password)

# Delete an existing item
kr.delete_password("my-password-item", "my-username")
```

### Using a specific vault
If you want to use a specific vault, edit your `keyringrc.cfg` file located in `keyring.util.platform_.config_root()` (typically `$env:LOCALAPPDATA\Python Keyring\keyringrc.cfg` on Windows) and add a section

```
[onepassword]
vault=MySuperSecretVault
```

## Caveats

This fork was made for personal use and is not guaranteed to work in all cases. Please use with caution, as I can't take responsibility for any issues that may arise from using this package.

`onepassword-keyring` was only tested with:
- macOS, using the `1password-cli` from `brew`

As mentioned, `onepassword-keyring` only works in the context of a CLI application with access to standard inputs and output.

## Licensing

`onepassword-keyring` is published under the terms of the [MIT License](LICENSE.md).

## Acknowledgment

This package is forked from and heavily based on [bitwarden-keyring](https://github.com/ewjoachim/bitwarden-keyring) by [ewjoachim](https://github.com/ewjoachim)