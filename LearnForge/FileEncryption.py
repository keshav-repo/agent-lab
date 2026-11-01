"""Local, authenticated file encryption helpers for BrowserAssistant."""

import os
import stat
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


_MAGIC = b"LFENC1"
_SALT_SIZE = 16
_NONCE_SIZE = 12
_TAG_SIZE = 16
_CHUNK_SIZE = 1024 * 1024
_HEADER_SIZE = len(_MAGIC) + _SALT_SIZE + _NONCE_SIZE


def _validated_source(path: str | Path) -> Path:
    source = Path(path).expanduser()
    if not source.is_absolute():
        raise ValueError("Please provide an absolute file path.")
    source = source.resolve(strict=True)
    if not source.is_file():
        raise ValueError("The path must refer to a regular file.")
    return source


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    if not passphrase:
        raise ValueError("Passphrase cannot be empty.")
    return Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(
        passphrase.encode("utf-8")
    )


def is_encrypted_file(path: str | Path) -> bool:
    """Return whether the file starts with this module's encrypted-file marker."""
    with Path(path).open("rb") as source:
        return source.read(len(_MAGIC)) == _MAGIC


def _replace_contents_atomically(destination: Path, writer) -> None:
    """Write a private temporary file, then atomically replace the source file."""
    source_stat = destination.stat()
    if source_stat.st_nlink > 1:
        raise ValueError("Refusing in-place encryption of a file with multiple hard links.")
    original_mode = stat.S_IMODE(source_stat.st_mode)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(fd, "wb") as temporary_file:
            writer(temporary_file)
            os.fchmod(temporary_file.fileno(), original_mode)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_name, destination)
    finally:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


def encrypt_file(path: str | Path, passphrase: str) -> Path:
    """Encrypt a file in place, preserving its original filename."""
    source = _validated_source(path)
    salt = os.urandom(_SALT_SIZE)
    nonce = os.urandom(_NONCE_SIZE)
    header = _MAGIC + salt + nonce
    encryptor = Cipher(algorithms.AES(_derive_key(passphrase, salt)), modes.GCM(nonce)).encryptor()
    encryptor.authenticate_additional_data(header)

    def write_encrypted(output) -> None:
        output.write(header)
        with source.open("rb") as input_file:
            while chunk := input_file.read(_CHUNK_SIZE):
                output.write(encryptor.update(chunk))
        output.write(encryptor.finalize())
        output.write(encryptor.tag)

    _replace_contents_atomically(source, write_encrypted)
    return source


def decrypt_file(path: str | Path, passphrase: str) -> Path:
    """Decrypt an encrypted file in place, preserving its filename."""
    source = _validated_source(path)
    file_size = source.stat().st_size
    if file_size < _HEADER_SIZE + _TAG_SIZE:
        raise ValueError("The encrypted file is incomplete or invalid.")

    with source.open("rb") as input_file:
        header = input_file.read(_HEADER_SIZE)
        if len(header) != _HEADER_SIZE or not header.startswith(_MAGIC):
            raise ValueError("Unrecognized encrypted file format.")
        salt_start = len(_MAGIC)
        salt = header[salt_start:salt_start + _SALT_SIZE]
        nonce = header[salt_start + _SALT_SIZE:]
        input_file.seek(-_TAG_SIZE, os.SEEK_END)
        tag = input_file.read(_TAG_SIZE)
        ciphertext_size = file_size - _HEADER_SIZE - _TAG_SIZE
        input_file.seek(_HEADER_SIZE)

        decryptor = Cipher(
            algorithms.AES(_derive_key(passphrase, salt)), modes.GCM(nonce, tag)
        ).decryptor()
        decryptor.authenticate_additional_data(header)

        def write_decrypted(output) -> None:
            remaining = ciphertext_size
            while remaining:
                chunk = input_file.read(min(_CHUNK_SIZE, remaining))
                if not chunk:
                    raise ValueError("The encrypted file is truncated.")
                remaining -= len(chunk)
                output.write(decryptor.update(chunk))
            output.write(decryptor.finalize())

        try:
            _replace_contents_atomically(source, write_decrypted)
        except InvalidTag as exc:
            raise ValueError("Wrong passphrase or encrypted file authentication failed.") from exc

    return source
