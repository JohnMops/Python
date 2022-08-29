from kubernetes import client, config
import os
import parser.parser as parser
import pprint
import functions.functions as funcs
from termcolor import colored

kubeconfig = os.environ.get('KUBECONFIG')
if kubeconfig is None:
    print(colored("No 'KUBECONFIG' environment variable specified", "red"))
    exit(0)


def main():
    parse = parser.Parser()
    args = parse.get()
    if not args.select:
        funcs.deployment_info_all(kubeconfig, args)
        funcs.find_service(kubeconfig, args)
    else:
        funcs.switch(kubeconfig, args)

if __name__ == '__main__':
    main()
