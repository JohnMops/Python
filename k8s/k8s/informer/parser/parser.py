import argparse


class Parser():
    def __init__(self):
        self.__parser = argparse.ArgumentParser(
            description='Take arguments for fetching information in a k8s cluster'
        )
        self.__parser.add_argument('--deployment-name', '-d', required=True, type=str, help='Deployment name')
        self.__parser.add_argument('--namespace', '-n', required=True, type=str, help='Namespace name')
        self.__parser.add_argument('--select', required=False,
                                   nargs='*',
                                   default=[],
                                   choices=['basic', 'ports', 'volumes', 'service', 'resources', 'affinity',
                                            'hpa'],
                                   help='Choose what information to fetch')

    def get(self):
        args = self.__parser.parse_args()
        return args
