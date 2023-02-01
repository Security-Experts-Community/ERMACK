"""CPE Wrapper"""

from cpe.cpe2_3_fs import CPE2_3_FS as cpe_fs
from cpe.cpelang2_3 import CPELanguage2_3 as cpe_lang
from cpe.cpeset2_3 import CPESet2_3 as cpe_set

from ermack.entities.infrastructure_profile import InfrastructureProfile
from ermack.entities.response_action_implementation import ResponseActionImpl


def __create_cpe_expression(cpe_names: list) -> str:
    expression = """<?xml version="1.0" encoding="UTF-8"?>
<cpe:platform-specification xmlns:cpe="http://cpe.mitre.org/language/2.0">
    <cpe:platform id="1">
        <cpe:title>CPE Expression</cpe:title>
        <cpe:logical-test operator="AND" negate="FALSE">"""
    for cpe_name in cpe_names:
        expression += f'''
            <cpe:fact-ref name="{cpe_name}"/>"'''
    expression += """
        </cpe:logical-test>
    </cpe:platform>
</cpe:platform-specification>
"""
    return expression


def __contains_requirements(impl: ResponseActionImpl):
    return "requirements" in impl.view and impl.view["requirements"] is not None


def __contains_software_requirements(impl: ResponseActionImpl) -> bool:
    return __contains_requirements(impl) and "software" in impl.view["requirements"]


def __means_contains_cpe(software: dict):
    return (
        "means_of_action" in software
        and software["means_of_action"] is not None
        and len(software["means_of_action"]) > 0
        and "cpe-fs" in software["means_of_action"][0]
    )


def __targets_contains_cpe(software: dict):
    return (
        "targets_of_action" in software
        and software["targets_of_action"] is not None
        and len(software["targets_of_action"]) > 0
        and "cpe-fs" in software["targets_of_action"][0]
    )


def __contains_means_or_targets(impl: ResponseActionImpl) -> bool:
    if __contains_software_requirements(impl):
        software = impl.view["requirements"]["software"]
        return __means_contains_cpe(software) or __targets_contains_cpe(software)
    else:
        return False


def __check_requirements(impl: ResponseActionImpl):
    return __contains_means_or_targets(impl)


def __get_cpe_names_from_impl(impl: ResponseActionImpl) -> list:
    cpe_names = []
    software = impl.view["requirements"]["software"]
    if __means_contains_cpe(software):
        for soft in software["means_of_action"]:
            cpe_names.append(soft["cpe-fs"])

    if __targets_contains_cpe(software):
        for soft in software["targets_of_action"]:
            cpe_names.append(soft["cpe-fs"])
    return cpe_names


# TODO: cover with tests
def check_applicability_of_impl(
    infrastructure_profile: InfrastructureProfile, impl: ResponseActionImpl
) -> bool:
    """Check if action implementation applicable for current infrastructure profile

    :param infrastructure_profile: Infrastructure Profile entity
    :type infrastructure_profile: InfrastructureProfile
    :param impl: Implementation of response action
    :type impl: ResponseActionImpl
    :return: True if applicable
    :rtype: bool
    """
    if __check_requirements(impl):
        cpe_names = __get_cpe_names_from_impl(impl)
        impl_cpe = cpe_lang(__create_cpe_expression(cpe_names))
        set_of_cpe = cpe_set()
        profile = infrastructure_profile.data()["software_profile"]
        for entry in profile:
            if "cpe-fs" in entry and entry["cpe-fs"] != "":
                set_of_cpe.append(cpe_fs(entry["cpe-fs"]))
        return impl_cpe.language_match(set_of_cpe)
    return False
