#!/usr/bin/env python3
"""Backward-compatible setup script
"""

import codecs
import os
import re
import sys

try:
    from setuptools import setup
    USING_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    USING_SETUPTOOLS = False

try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser
    from collections import MutableMapping  # 2.6

    class RawConfigParser(RawConfigParser, MutableMapping):
        """ConfigParser that does not do interpolation

        Emulate dictionary-like access.
        """
        class Section(MutableMapping):
            """A single section from a parser
            """
            def __init__(self, config, section):
                self.config = config
                self.section = section

            def __getitem__(self, option):
                if self.config.has_option(self.section, option):
                    return self.config.get(self.section, option)
                raise KeyError(option)

            def __setitem__(self, option, value):
                self.config.set(self.section, option, value)

            def __delitem__(self, option):
                self.config.remove_option(self.section, option)

            def __iter__(self):
                return iter(self.config.options(self.section))

            def __len__(self):
                return len(self.config.options(self.section))

        def __getitem__(self, section):
            if self.has_section(section):
                return RawConfigParser.Section(self, section)
            raise KeyError(section)

        def __setitem__(self, section, value):
            if self.has_section(section):
                self.remove_section(section)
            self.add_section(section)
            for key in value:
                self.set(section, key, value[key])

        def __delitem__(self, section):
            self.remove_section(section)

        def __iter__(self):
            return iter(self.sections())

        def __len__(self):
            return len(self.sections())

LIB_DIR = os.path.join("build", "lib")

if os.name in set(["posix"]):
    try:
        from multiprocessing import cpu_count
    except (ImportError, NotImplementedError):
        pass

MULTI_OPTIONS = set([
    ("global", "commands"),
    ("global", "compilers"),
    ("global", "setup_hooks"),
    ("metadata", "platform"),
    ("metadata", "supported-platform"),
    ("metadata", "classifier"),
    ("metadata", "requires-dist"),
    ("metadata", "provides-dist"),
    ("metadata", "obsoletes-dist"),
    ("metadata", "requires-external"),
    ("metadata", "project-url"),
    ("files", "packages"),
    ("files", "modules"),
    ("files", "scripts"),
    ("files", "package_data"),
    ("files", "data_files"),
    ("files", "extra_files"),
    ("files", "resources"),
])

ENVIRON_OPTIONS = set([
    ("metadata", "classifier"),
    ("metadata", "requires-dist"),
    ("metadata", "provides-dist"),
    ("metadata", "obsoletes-dist"),
    ("metadata", "requires-python"),
    ("metadata", "requires-external"),
])

# For environment markers
import platform #@UnusedImport

python_version = "%s.%s" % sys.version_info[:2]
python_full_version = sys.version.split()[0]


def which(program, win_allow_cross_arch=True):
    """Identify the location of an executable file.
    """
    def is_exe(path):
        return os.path.isfile(path) and os.access(path, os.X_OK)

    def _get_path_list():
        return os.environ["PATH"].split(os.pathsep)

    if os.name == "nt":
        def find_exe(program):
            root, ext = os.path.splitext(program)
            if ext:
                if is_exe(program):
                    return program
            else:
                for ext in os.environ["PATHEXT"].split(os.pathsep):
                    program_path = root + ext.lower()
                    if is_exe(program_path):
                        return program_path
            return None

        def get_path_list():
            paths = _get_path_list()
            if win_allow_cross_arch:
                alt_sys_path = os.path.expandvars(r"$WINDIR\Sysnative")
                if os.path.isdir(alt_sys_path):
                    paths.insert(0, alt_sys_path)
                else:
                    alt_sys_path = os.path.expandvars(r"$WINDIR\SysWOW64")
                    if os.path.isdir(alt_sys_path):
                        paths.append(alt_sys_path)
            return paths

    else:
        def find_exe(program):
            return program if is_exe(program) else None

        get_path_list = _get_path_list

    if os.path.split(program)[0]:
        program_path = find_exe(program)
        if program_path:
            return program_path
    else:
        for path in get_path_list():
            program_path = find_exe(os.path.join(path, program))
            if program_path:
                return program_path
    return None


def split_multiline(value):
    """Split a multiline string into a list, excluding blank lines.
    """
    return [element for element in (line.strip() for line in value.split("\n"))
            if element]


def split_elements(value):
    """Split a string with comma or space-separated elements into a list.
    """
    l = [v.strip() for v in value.split(",")]
    if len(l) == 1:
        l = value.split()
    return l


def eval_environ(value):
    """Evaluate environment markers.
    """
    def eval_environ_str(value):
        parts = value.split(";")
        if len(parts) < 2:
            return value
        expr = parts[1].lstrip()
        if not re.match("^((\\w+(\\.\\w+)?|'.*?'|\".*?\")\\s+"
                        "(in|==|!=|not in)\\s+"
                        "(\\w+(\\.\\w+)?|'.*?'|\".*?\")"
                        "(\s+(or|and)\s+)?)+$", expr):
            raise ValueError("bad environment marker: %r" % expr)
        expr = re.sub(r"(platform\.\w+)", r"\1()", expr)
        return parts[0] if eval(expr) else ""

    if isinstance(value, list):
        new_value = []
        for element in value:
            element = eval_environ_str(element)
            if element:
                new_value.append(element)
    elif isinstance(value, str):
        new_value = eval_environ_str(value)
    else:
        new_value = value

    return new_value


def get_cfg_value(config, section, option):
    """Get configuration value.
    """
    try:
        value = config[section][option]
    except KeyError:
        if (section, option) in MULTI_OPTIONS:
            return []
        else:
            return ""
    if (section, option) in MULTI_OPTIONS:
        value = split_multiline(value)
    if (section, option) in ENVIRON_OPTIONS:
        value = eval_environ(value)
    return value


def set_cfg_value(config, section, option, value):
    """Set configuration value.
    """
    if isinstance(value, list):
        value = "\n".join(value)
    config[section][option] = value


def get_package_data(value):
    package_data = {}
    firstline = True
    prev = None
    for line in value:
        if "=" in line:
            # package name -- file globs or specs
            key, value = line.split("=")
            prev = package_data[key.strip()] = value.split()
        elif firstline:
            # invalid continuation on the first line
            raise ValueError(
                'malformed package_data first line: %r (misses "=")' %
                line)
        else:
            # continuation, add to last seen package name
            prev.extend(line.split())
        firstline = False
    return package_data


def get_data_files(value):
    data_files = []
    for data in value:
        data = data.split("=")
        if len(data) != 2:
            continue
        key, value = data
        values = [v.strip() for v in value.split(",")]
        data_files.append((key, values))
    return data_files


def read_description_file(config):
    filenames = get_cfg_value(config, "metadata", "description-file")
    if not filenames:
        return ""
    value = []
    for filename in filenames.split():
        f = codecs.open(filename, encoding="utf-8")
        try:
            value.append(f.read())
        finally:
            f.close()
    return "\n\n".join(value).strip()


def cfg_to_args(config):
    """Compatibility helper to use setup.cfg in setup.py.
    """
    kwargs = {}
    opts_to_args = {
        "metadata": [
            ("name", "name"),
            ("version", "version"),
            ("author", "author"),
            ("author-email", "author_email"),
            ("maintainer", "maintainer"),
            ("maintainer-email", "maintainer_email"),
            ("home-page", "url"),
            ("summary", "description"),
            ("description", "long_description"),
            ("download-url", "download_url"),
            ("classifier", "classifiers"),
            ("platform", "platforms"),
            ("license", "license"),
            ("keywords", "keywords"),
        ],
        "files": [
            ("packages_root", "package_dir"),
            ("packages", "packages"),
            ("modules", "py_modules"),
            ("scripts", "scripts"),
            ("package_data", "package_data"),
            ("data_files", "data_files"),
        ],
    }

    if USING_SETUPTOOLS:
        opts_to_args["metadata"].append(("requires-dist", "install_requires"))
        kwargs["zip_safe"] = False

    for section in opts_to_args:
        for option, argname in opts_to_args[section]:
            value = get_cfg_value(config, section, option)
            if value:
                if argname in kwargs:
                    kwargs[argname] += value
                else:
                    kwargs[argname] = value

    if "long_description" not in kwargs:
        kwargs["long_description"] = read_description_file(config)

    if "package_dir" in kwargs:
        kwargs["package_dir"] = {"": kwargs["package_dir"]}

    if "keywords" in kwargs:
        kwargs["keywords"] = split_elements(kwargs["keywords"])

    if "package_data" in kwargs:
        kwargs["package_data"] = get_package_data(kwargs["package_data"])

    if "data_files" in kwargs:
        kwargs["data_files"] = get_data_files(kwargs["data_files"])

    return kwargs

def load_config(file="setup.cfg"):
    config = RawConfigParser()
    config.optionxform = lambda x: x.lower().replace("_", "-")
    config.read(file)
    return config


def main():
    """Running with distutils or setuptools
    """
    config = load_config()
    setup(**cfg_to_args(config))


if __name__ == "__main__":
    sys.exit(main())
