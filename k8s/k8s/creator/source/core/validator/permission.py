
import re
import os
import csv

import common

logger = common.Logger(__name__)

class Permission:
    def __init__(self):
        rules_file_path = self.__get_rules_file_path()

        self.__rules = []
        with open(rules_file_path, 'r') as rules_file:
            rules = csv.DictReader(rules_file, delimiter=" ", skipinitialspace=True, fieldnames=['action','regex'])

            for rule in rules:
                if rule['action'].lower() == 'allow':
                    action = True
                elif rule['action'].lower() == 'deny':
                    action = False
                else:
                    raise common.Exception(logger, f"Invalid action for rule {rule}")

                regex = rule['regex']

                self.__rules.append({'action': action, 'regex': regex})

        logger.info(f'Rules files loaded: {rules_file_path}')

    def __get_rules_file_path(self):
        if 'RULES_FILE_PATH' not in os.environ:
            raise common.Exception(logger, "Missing environment variable RULES_FILE_PATH")

        rules_file_path = os.environ['RULES_FILE_PATH']

        return rules_file_path

    def match(self, permission):
        for rule in self.__rules:
            if re.match(rule["regex"], permission):
                return rule['action']

        raise common.Exception(logger, f"No rule matched for permission: {permission}")

    @staticmethod
    def validate(permissions):
        validatorPermission = Permission()
        for permission in permissions:
            if not validatorPermission.match(permission):
                raise common.Exception(logger, f"Validation failed for permission: {permission}")