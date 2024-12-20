from base64 import b64decode
import os
import uuid
from graphql import GraphQLError

from global_config import OTHER_MAX_SIZE, VIDEO_MAX_SIZE


class FileHandling:
    def __init__(self):
        pass

    def convert_KB_to_MB(self, size: int) -> int:
        return int(size / (1024 * 1024))

    def validate_file_size(self, file_extension: str, file_size: int) -> bool:
        if file_extension.lower() in [".svg", ".jpg", ".jpeg", ".png", ".gif"]:
            if file_size > OTHER_MAX_SIZE:
                raise GraphQLError(f"Image files must be under {self.convert_KB_to_MB(OTHER_MAX_SIZE)}MB.")
        elif file_extension.lower() in [
            ".wav",
            ".mpeg",
            ".mp3",
            ".aac",
            ".aacp",
            ".ogg",
            ".webm",
            ".flac",
            ".m4a",
        ]:
            if file_size > OTHER_MAX_SIZE:
                raise GraphQLError(f"Audio files must be under {self.convert_KB_to_MB(OTHER_MAX_SIZE)}MB.")
        elif file_extension.lower() in [".mp4", ".webm", ".opgg", ".3gp", ".flv"]:
            if file_size > VIDEO_MAX_SIZE:
                raise GraphQLError(f"Video files must be under {self.convert_KB_to_MB(VIDEO_MAX_SIZE)}MB.")
        else:
            raise GraphQLError("Unsupported file format.")

    def upload_file(
        self,
        base64: str,
        file_name: str,
        absolute_path: str,
        storage_path: str,
        sub_path: str,
    ) -> str:

        filename, file_extension = os.path.splitext(file_name)
        unique_filename = uuid.uuid4().hex + filename + file_extension
        media_directory = os.path.join(absolute_path, storage_path, sub_path)
        if not os.path.exists(media_directory):
            os.makedirs(media_directory)
        file_data = b64decode(base64.split(",")[1])
        file_size = len(file_data)
        self.validate_file_size(file_extension, file_size)

        self.write_file(base64, os.path.join(media_directory, unique_filename))

        return os.path.join(sub_path, unique_filename)

    def write_file(self, base64: str, path: str):
        with open(path, "wb") as fh:
            fh.write(b64decode(base64.split(",")[1]))

    def delete_file(self, path: str):
        if os.path.exists(path):
            os.remove(path)