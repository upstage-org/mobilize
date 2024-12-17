from graphql import GraphQLError


def validate_file_size(file_extension: str, file_size: int) -> bool:
    video_max_size = 300 * 1024 * 1024
    other_max_size = 1 * 1024 * 1024
    if file_extension.lower() in [".svg", ".jpg", ".jpeg", ".png", ".gif"]:
        if file_size > other_max_size:
            raise GraphQLError("Image files must be under 1MB.")
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
        if file_size > other_max_size:
            raise GraphQLError("Audio files must be under 1MB.")
    elif file_extension.lower() in [".mp4", ".webm", ".opgg", ".3gp", ".flv"]:
        if file_size > video_max_size:
            raise GraphQLError("Video files must be under 300MB.")
    else:
        raise GraphQLError("Unsupported file format.")
