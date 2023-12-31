import collections.abc
import os
from pprint import pprint
from typing import Any, Iterable
from .optclass import DownloadInfo, RepositoryInfo, OptInfo
import yaml
import re

__all__ = ["YamlConfigLoader"]

class YamlConfigLoader():
    """ 
    Loader for the yaml config file. 
    
    usage: opt_dict, cst_dict = YamlConfigLoader().load("SCRIPT_PATH")
    
    The ``opt_dict`` is a dictionary of OptInfo objects holding all the options 
    for the user to choose.
    
    The ``cst_dict`` is a dictionary of constant strings. Those constants will
    are used by the installer to replace the values in the yaml. and all the 
    string of the yaml file will be recursively replaced by the values of 
    the constants. It allow to use constants in constant declaration. 
    To be treated as a replaceable constant, the string must be 
    between dollar signs `$`.
    """
    def __init__(self,):

        self._yaml_dict: dict[str, Any] = {}

        # auto add cst key for `#` replacement in the yml string
        self._cst_dict: dict[str, str] = {}
        self._opt_dict: dict[str, Any] = {}

    @property
    def opt_dict(self):
        """
        Returns a copy of the opt dictionary.
        """
        return self._opt_dict.copy()

    @property
    def cst_dict(self):
        """
        Returns a copy of the constant dictionary.
        """
        return self._cst_dict.copy()

    def load(
        self, 
        config_directory
        ) -> tuple[dict[str, list[OptInfo]], dict[str, str]]:
        """
        Load the YAML files from the given directory and return 
        the opt and the constant dictionary.
        
        """
        self._yaml_dict = self._load_yml_files(config_directory)       

        for key, sub_dict in self._yaml_dict.items():
            if '.cst' in key:
                self._cst_dict.update(sub_dict)
            else:
                self._opt_dict[key] = sub_dict

        self._recursive_cst()
        """Recursively process the cst dictionary."""
        
        # Create a regular expression from the dictionary keys
        # https://stackoverflow.com/questions/15175142/how-can-i-do-multiple-substitutions-using-regex
        self._cst_regex = re.compile(
            "(%s)" % "|".join(map(re.escape, self._cst_dict.keys())))

        self._cst_replace_in_opt_dict()

        for file, sub_dict in self._opt_dict.items():
            self._opt_dict[file] = [self._optinfo_from_dict(v) for v in sub_dict.values()]

        return self._opt_dict, self._cst_dict

    def _optinfo_from_dict(self, source: dict) -> OptInfo:
        """ Create an OptInfo object from a yaml dictionary."""

        repos_list = []
        file_list = []

        for repos in source.get('repos', ()):
            for r in repos.values():
                if r:
                    repos_list.append(RepositoryInfo(**r))

        for files in source.get('files', ()):
            for f in files.values():
                if f:
                    file_list.append(DownloadInfo(**f))

        return OptInfo(
            name=source["name"],
            description=source.get("description", ""),
            default=source.get("default", False),
            repos=tuple(repos_list),
            files=tuple(file_list),
            cmd=tuple(source.get('cmd', ())),
        )

    def _recursive_cst(self):
        """  recursively replaced by the values of the constants. 
        It allow to use constants in constant declaration """
        for k, v in self._cst_dict.items():
            if not isinstance(v, str):
                self._cst_dict[k] = str(v)

        while 1:
            remaining = 0
            for k, v in self._cst_dict.items():
                ns, nb_reps = re.subn(
                    r'''\$(\w+)\$''',
                    lambda match: self._cst_dict.get(match.group(1), ''),
                    v)

                if nb_reps:
                    self._cst_dict[k] = ns
                remaining += nb_reps

            if not remaining:
                break

        self._cst_dict = {f"${k}$": v for k, v in self._cst_dict.items()}

    def _cst_replace_in_opt_dict(self):

        def replace_item(obj):

            if isinstance(obj, dict):
                for k, v in obj.items():
                    obj[k] = replace_item(v)
                return obj

            elif isinstance(obj, str):
                return self._cst_regex.sub(
                    lambda mo: self._cst_dict[mo.string[mo.start():mo.end()]], obj)

            elif isinstance(obj, Iterable):
                return [replace_item(el) for el in obj]

            else:
                return obj

        self._opt_dict = replace_item(self._opt_dict)  # type: ignore

    def _load_yml_files(self, config_directory: str):
        yaml_dict = {}

        for file_name in os.listdir(config_directory):
            if file_name.endswith(".yml") or file_name.endswith(".yaml"):
                file_path = os.path.join(config_directory, file_name)
                basename = os.path.splitext(file_name)[0]
                basename = basename.replace('_', ' ')

                with open(file_path, "r") as file:
                    yaml_data = yaml.safe_load(file)
                    yaml_dict[basename] = yaml_data

        return yaml_dict

    def items(self):
        return self._opt_dict.items()

    def keys(self):
        return self._opt_dict.keys()

    def values(self):
        return self._opt_dict.values()
