#!/usr/bin/env python3

"""Class for handling the project configuration"""

import re
import warnings

import requests
import yaml
from atlassian.confluence import Confluence

# Default configuration file path
DEFAULT_CONFIG_PATH = "config.yml"

# Show warnings only once:
with warnings.catch_warnings():
    warnings.simplefilter("once")


class Configuration:
    """Class for handling the project configuration"""

    def __init__(self, path=DEFAULT_CONFIG_PATH):
        """Creation Config object holding the project configuration

        :param path: path to the configuration file
        :type item: str
        """
        self.config_file = path
        self.set_config(path=path)

    def get_config(self):
        """Get the configuration as defined by the project

        :return: dictionary with project configuration
        :rtype: dict
        """
        return self.__config

    def set_config(self, path):
        """Set the project configuration via file path

        Arguments:
            path {str} -- File location of the config (yaml)
        """
        self.__config = dict(self.__read_yaml_file(path))

    def __read_yaml_file(self, path):
        """
        Open the yaml file and load it to the variable.

        :param path: path to a file
        :type item: str
        :return: yaml content as dictionary
        :rtype: dict
        """
        with open(path) as f:
            yaml_fields = yaml.load_all(f.read(), Loader=yaml.FullLoader)

        buff_results = list(yaml_fields)
        if len(buff_results) > 1:
            result = buff_results[0]
            result["additions"] = buff_results[1:]
        else:
            result = buff_results[0]

        return result

    @property
    def config(self) -> dict:
        """Property to get configuration dictionary

        :return: configuration dictionary
        :rtype: dict
        """
        return self.get_config()


# Initialize global config
Config = Configuration()


class Utils:
    """Class which consists of handful methods used throughout the project"""

    @staticmethod
    def read_text_file(path):
        """Open the file and load it to the variable. Return text"""
        with open(path, mode="r", encoding="utf-8") as f:
            rule_text = f.read()

        return rule_text

    @staticmethod
    def read_yaml_file(path):
        """Load yaml file to the variable.

        :return: dictionary with yaml file content
        :rtype: dict
        """
        if path == "config.yml":
            wrn = "Use 'load_config' or 'Config' instead for config"
            # Warning will not show,
            # unless captured by logging facility or python called with -Wd
            warnings.warn(message=wrn, category=DeprecationWarning)
            return Config.config

        with open(path, encoding="utf-8", mode="r") as f:
            yaml_fields = yaml.load_all(f.read(), Loader=yaml.FullLoader)

        buff_results = list(yaml_fields)
        if len(buff_results) > 1:
            result = buff_results[0]
            result["additions"] = buff_results[1:]
        else:
            result = buff_results[0]
        return result

    @staticmethod
    def parse_yaml_from_string(yaml_string):
        """Parse yaml string to dictionary

        :param yaml_string: string with yaml fields
        :type yaml_string: str
        :return: dictionary with yaml string content
        :rtype: dict
        """
        return yaml.safe_load(yaml_string)

    @staticmethod
    def load_config(path):
        """Load the configuration file into a dictionary

        :return: dictionary with configuration
        :rtype: dict
        """
        return Configuration(path).config

    @staticmethod
    def write_file(path: str, content: str, options="w+") -> bool:
        """Write content to some file

        :param path: path to write
        :type path: str
        :param content: content to write
        :type content: str
        :return: status of the operation
        :rtype: bool
        """
        with open(path, options, encoding="utf-8") as file:
            file.write(content)
        return True

    @staticmethod
    def confluence_get_page_id(apipath: Confluence, auth, space, title):
        """Get confluence page ID based on title and space

        :return: _description_
        :rtype: _type_
        """
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        url = apipath + "content"
        space_page_url = (
            url + "?spaceKey=" + space + "&title=" + title + "&expand=space"
        )

        if isinstance(auth, str):
            headers["Authorization"] = f"Bearer {auth}"
            response = requests.request("GET", space_page_url, headers=headers)
        else:
            response = requests.request(
                "GET", space_page_url, headers=headers, auth=auth
            )

        if response.status_code == 401:
            print(
                "Unauthorized Response. Try to use a token instead of a password. "
                + "Follow the guideline for more info: \n"
                + "https://developer.atlassian.com/cloud/confluence/basic-auth-"
                + "for-rest-apis/#supplying-basic-auth-headers"
            )
            exit()
        else:
            response = response.json()

        # Check if response contains proper information and return it if so
        if response.get("results"):
            if isinstance(response["results"], list):
                if response["results"][0].get("id"):
                    return response["results"][0]["id"]

        # If page not found
        return None

    @staticmethod
    def normalize_react_title(title: str, fmtrules: dict) -> str:
        """Normalize title if it is a RA/RP title in the following format:

        RP_0003_identification_make_sure_email_is_a_phishing
        """
        react_id_re = re.compile(r"R[AP]_\d{4}_.*$")
        if react_id_re.match(title):
            title = title[8:].split("_", 0)[-1].replace("_", " ").capitalize()
            new_title = ""
            for word in title.split():
                if word.lower() in fmtrules["abbreviations"]:
                    new_title += word.upper()
                    new_title += " "
                    continue
                elif word.lower() in fmtrules["capitalizeWords"]:
                    new_title += word.capitalize()
                    new_title += " "
                    continue
                new_title += word
                new_title += " "
            return new_title.strip()
        return title
