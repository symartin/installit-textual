import dataclasses
import re
from typing import TYPE_CHECKING, Any, Optional
import dataclasses

    
__all__ = ["DownloadInfo", "RepositoryInfo", "OptInfo"]


@dataclasses.dataclass(frozen=True, eq=True)
class DownloadInfo:
    """ Info on one file to download """
    url: str
    path:str
    name: str = ""
    # MD5: Optional[str] = None
    # SHA1: Optional[str] = None
    # SHA256: Optional[str] = None

@dataclasses.dataclass(frozen=True, eq=True)
class RepositoryInfo:
    """ Info on one git repository """
    url: str
    path:str
    name: str = ""
    submodule: bool = False

@dataclasses.dataclass(frozen=True, eq=True)
class OptInfo:
    """ A dataclass to hold all the  information in a `opt`"""
    
    name: str
    description: str = ""
    """ description of the option, will be interpreted as markdown """
    
    default: bool = False
    """ if true this option is selected by default """
    
    repos: Optional[tuple[RepositoryInfo]]= None
    files: Optional[tuple[DownloadInfo]] = None
    cmd: Optional[tuple[str]] = None
    



        

        