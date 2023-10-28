from enum import Enum


class CompressionType(str, Enum):
    none = "none"
    zip = "zip"
    tar = "tar"
    seven_z = "7z"


class OrderByType(str, Enum):
    ascending = "asc"
    descending = "desc"
