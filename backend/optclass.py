import dataclasses
import re
from typing import TYPE_CHECKING, Any, Optional
import dataclasses

    
__all__ = ["DownloadInfo", "RepositoryInfo", "OptInfo"]


@dataclasses.dataclass(frozen=True, eq=True)
class DownloadInfo:
    url: str
    path:str
    name: str = ""
    # MD5: Optional[str] = None
    # SHA1: Optional[str] = None
    # SHA256: Optional[str] = None

@dataclasses.dataclass(frozen=True, eq=True)
class RepositoryInfo:
    url: str
    path:str
    name: str = ""
    submodule: bool = False

@dataclasses.dataclass(frozen=True, eq=True)
class OptInfo:
    """ a data class to hold the base information """
    name: str
    description: str = ""
    default: bool = False
    """ if true this option is selected by default """
    repos: Optional[tuple[RepositoryInfo]]= None
    files: Optional[tuple[DownloadInfo]] = None
    cmd: Optional[tuple[str]] = None
    



        

        