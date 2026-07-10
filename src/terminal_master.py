
import os
import shlex
from subprocess import call
import tempfile

from src.config_model import Config


class TerminalMaster:
    def __init__(self, config: Config) -> None:
        self.config = config


    def openVIM(self, init_msg=""):
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(init_msg.encode("utf-8"))
            tf.flush()

            editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vim"
            call(shlex.split(editor) + [tf.name])

            tf.seek(0)
            edited_message = tf.read().decode("utf-8")

        return edited_message
