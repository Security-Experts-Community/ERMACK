#!/usr/bin/env python3

"""Module responsible for download current version of MITRE ATTACK Matrix"""

import json

import requests

from .utils import Utils as utils

config = utils.load_config("config.yml")
attack_json_url = config.get("attack_json_url")
attack_mapping_path = config.get("attack_mapping_path")


class UpdateAttackMapping:
    """Download and extract Tactics, Techniques and Mitigations"""

    def __init__(self):
        """Do update"""
        ta_mapping = {}
        te_mapping = {}
        mi_mapping = {}

        enterprise_attack_json = requests.get(attack_json_url).json()

        for attack_object in enterprise_attack_json["objects"]:
            if self.__is_mitigation(attack_object):
                mitigation_id = self.__get_id(attack_object)
                mitigation_name = attack_object["name"]
                mi_mapping.update({mitigation_id: mitigation_name})
            elif attack_object["type"] == "attack-pattern":
                technique_id = self.__get_id(attack_object)
                technique_name = attack_object["name"]
                te_mapping.update({technique_id: technique_name})
            elif attack_object["type"] == "x-mitre-tactic":

                tactic_id = self.__get_id(attack_object)
                tactic_name = attack_object["name"]
                tactic_tag = "attack." + attack_object["name"].lower().replace(" ", "_")
                ta_mapping[tactic_tag] = [tactic_name, tactic_id]

        with open(attack_mapping_path, "w") as fp:
            fp.write("ta_mapping = " + json.dumps(ta_mapping, indent=4) + "\n")
            fp.write("te_mapping = " + json.dumps(te_mapping, indent=4) + "\n")
            fp.write("mi_mapping = " + json.dumps(mi_mapping, indent=4))
            print("[✓] ATT&CK mapping has been updated")

    def __is_course_of_action(self, attack_object):
        return attack_object["type"] == "course-of-action"

    def __get_id(self, attack_object):
        return attack_object["external_references"][0]["external_id"]

    def __is_mitigation(self, attack_object):
        return self.__is_course_of_action(attack_object) and "M" in self.__get_id(
            attack_object
        )
