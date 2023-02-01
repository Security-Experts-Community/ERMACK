import os

from ermack.entities.response_action import ResponseAction
from ermack.utils.utils import Utils as utils

config = utils.load_config("config.yml")


def test_check_all_entities():
    base_data_dir = config.get("data_base_dir")
    locales_list = os.listdir(base_data_dir)
    lang = config.get("default_localization_lang")
    if lang not in locales_list:
        lang = "en"
    e_dir = config.get("response_actions_dir")
    e_list = [
        f.name for f in os.scandir(f"{base_data_dir}/{lang}/{e_dir}") if f.is_dir()
    ]

    mandatory_fields = ResponseAction.get_mandatory_fields()
    for e_file in e_list:
        response_action = ResponseAction.from_file(
            f"{base_data_dir}/{lang}/{e_dir}/{e_file}/{e_file}.yml"
        )
        assert response_action is not None
        for field in mandatory_fields:
            assert field in response_action.view
