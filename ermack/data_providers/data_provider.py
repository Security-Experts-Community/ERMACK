#!/usr/bin/env python3

"""Data rendering interface"""


class DataProvider:
    """TODO:"""

    def __init__(self) -> None:
        """TODO:"""
        pass

    def init_structure(self, with_root_page: bool = False) -> bool:
        """Interface method for initialization of entities structure

        :param with_root_page: parameter for Confluence renderer, defaults to False
        :type with_root_page: bool, optional
        :return: Status of creation
        :rtype: bool
        """
        pass

    def load_structure(self):
        """Interface method for loading entities structure"""
        pass

    # def set_parents(self) -> None:
    #     pass

    def create_actions_structure(self) -> bool:
        """Interface method for creating actions structure"""
        pass

    def write_entity(self, entity, title_with_id: bool = False):
        """Interface method for rendering entity

        :param entity: Entity to render
        :type entity: Entity
        :param title_with_id: If true, title will be prepended with entity ID
            , defaults to False
        :type title_with_id: bool, optional
        """
        pass

    def render_entities_table(self, entities: list):
        """Interface method for rendering entities list as table

        :param entities: Entities to render
        :type entities: list
        """
        pass
