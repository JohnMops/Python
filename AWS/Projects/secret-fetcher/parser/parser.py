import argparse


class Parser():
    def __init__(self):
        self.__parser = argparse.ArgumentParser(
            description='Automatically pull Secret Manager secrets and create environment variables from them'
        )
        self.__parser.add_argument('--secret-prefix', required=True, type=str, help='Delimited Secret Prefixes - "1,'
                                                                                    '2,3,4"')

    def get(self):
        args = self.__parser.parse_args()
        return args
