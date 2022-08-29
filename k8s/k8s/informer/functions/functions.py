import pprint
from kubernetes import client, config
import json
from termcolor import colored
import re


def deployment_info_all(kubeconfig, args):
    config.load_kube_config(config_file=kubeconfig)

    v1 = client.AppsV1Api()
    print(colored(f"Getting information about {args.deployment_name}...\n", 'green'))
    try:
        ret = v1.read_namespaced_deployment(namespace=args.namespace, name=args.deployment_name)
        deployment_basic_info(kubeconfig, args)
        deployment_info_volumes(kubeconfig, args)
        deployment_info_ports(kubeconfig, args)
        deployment_info_resources(kubeconfig, args)
        deployment_affinity_info(kubeconfig, args)
        deployment_info_hpa(kubeconfig, args)
    except client.exceptions.ApiException:
        print(colored(f"Deployment '{args.deployment_name}' not found ", "red"))


def deployment_affinity_info(kubeconfig, args):
    config.load_kube_config(config_file=kubeconfig)
    v1 = client.AppsV1Api()
    print(colored(f"Getting information about {args.deployment_name} Pods Allocation...\n", 'green'))
    try:
        ret = v1.read_namespaced_deployment(namespace=args.namespace, name=args.deployment_name)
        if ret.spec.template.spec.node_selector is not None:
            print(colored('Node Selector: ', "yellow"), end="")
            print(ret.spec.template.spec.node_selector)
        if ret.spec.template.spec.affinity is not None:
            print(colored('Node Affinity: ', "yellow"))
            pprint.pprint(ret.spec.template.spec.affinity.node_affinity)
            print(
                '------------------------------------------------------------------------------------------------------------------------')
            print(colored('Pod Affinity: ', "yellow"))
            pprint.pprint(ret.spec.template.spec.affinity.pod_affinity)
            print(
                '------------------------------------------------------------------------------------------------------------------------')
            print(colored('Pod Anti-Affinity: ', "yellow"))
            pprint.pprint(ret.spec.template.spec.affinity.pod_anti_affinity)
            print(
                '------------------------------------------------------------------------------------------------------------------------')
        print(
            '------------------------------------------------------------------------------------------------------------------------')
    except client.exceptions.ApiException:
        print(colored(f"Deployment '{args.deployment_name}' not found ", "red"))


def deployment_basic_info(kubeconfig, args):
    config.load_kube_config(config_file=kubeconfig)
    v1 = client.AppsV1Api()
    print(colored(f"Getting Basic information about {args.deployment_name}...\n", 'green'))
    try:
        ret = v1.read_namespaced_deployment(namespace=args.namespace, name=args.deployment_name)

        print(colored(f'Name: ', "yellow"), end="")
        print(ret.metadata.name)
        print(
            '------------------------------------------------------------------------------------------------------------------------')
        print(colored('Labels:\n', "yellow"))
        for k, v in ret.metadata.labels.items():
            print(f'{k}: {v}')
        print(
            '------------------------------------------------------------------------------------------------------------------------')
        for i in range(len(ret.spec.template.spec.containers)):
            print(colored(f'Container Name: ', "yellow"), end='')
            print(ret.spec.template.spec.containers[i].name)
            print(
                '------------------------------------------------------------------------------------------------------------------------')
            print(colored(f'Container Image:  ', "yellow"), end='')
            print(ret.spec.template.spec.containers[i].image)
            print(
                '------------------------------------------------------------------------------------------------------------------------')
    except client.exceptions.ApiException:
        print(colored(f"Deployment '{args.deployment_name}' not found ", "red"))


def deployment_info_resources(kubeconfig, args):
    config.load_kube_config(config_file=kubeconfig)
    v1 = client.AppsV1Api()
    print(colored(f"Getting information about {args.deployment_name} Resources...\n", 'green'))
    try:
        ret = v1.read_namespaced_deployment(namespace=args.namespace, name=args.deployment_name)
        for i in range(len(ret.spec.template.spec.containers)):
            print(colored(f'Container Resources:\n', "yellow"))
            if ret.spec.template.spec.containers[i].resources:
                pprint.pprint(f'Limits: {ret.spec.template.spec.containers[i].resources.limits}')
                pprint.pprint(f'Requests: {ret.spec.template.spec.containers[i].resources.requests}')
            else:
                print(colored(f"Resources Not Set", "red"))
            print(
                '------------------------------------------------------------------------------------------------------------------------')
    except client.exceptions.ApiException:
        print(colored(f"Deployment '{args.deployment_name}' not found ", "red"))


def deployment_info_hpa(kubeconfig, args):
    config.load_kube_config(config_file=kubeconfig)
    found = False
    v1 = client.AutoscalingV1Api()
    print(colored(f"Getting information about {args.deployment_name} HPA...\n", 'green'))
    try:
        ret = v1.list_namespaced_horizontal_pod_autoscaler(namespace=args.namespace)
        for i in ret.items:
            if i.spec.scale_target_ref.name == args.deployment_name:
                print(colored(f'Minimum Replicas: ', "yellow"), end="")
                print(i.spec.min_replicas)
                print(colored(f'Maximum Replicas: ', "yellow"), end="")
                print(i.spec.max_replicas)
                found = True
                print(
                    '------------------------------------------------------------------------------------------------------------------------')
                for k, b in i.metadata.labels.items():
                    if 'scaledobject.keda.sh' in k:
                        crd = client.CustomObjectsApi().list_cluster_custom_object(group="keda.sh",
                                                                                   version="v1alpha1",
                                                                                   plural='scaledobjects')
                        print(colored(f"Getting information about {args.deployment_name} Keda Object...\n", 'green'))
                        for o in range(len(crd['items'])):
                            if re.search(args.deployment_name, crd['items'][o]['metadata']['name']):
                                print(colored(f'Keda Scaled Object: ', "yellow"), end="")
                                print(crd['items'][o]['metadata']['name'])
                                print(
                                    '------------------------------------------------------------------------------------------------------------------------')
        if not found:
            print(colored(f"HPA for Deployment '{args.deployment_name}' not found ", "red"))
            print(
                '------------------------------------------------------------------------------------------------------------------------')

    except client.exceptions.ApiException:
        print(colored(f"Deployment '{args.deployment_name}' not found ", "red"))


def deployment_info_volumes(kubeconfig, args):
    config.load_kube_config(config_file=kubeconfig)

    v1 = client.AppsV1Api()
    print(colored(f"Getting information about {args.deployment_name} Volumes...\n", 'green'))
    try:
        ret = v1.read_namespaced_deployment(namespace=args.namespace, name=args.deployment_name)

        print(colored(f'Deployment Volumes: \n', "yellow"))
        if ret.spec.template.spec.volumes:
            for i in range(len(ret.spec.template.spec.volumes)):
                if ret.spec.template.spec.volumes[i].config_map:
                    print(colored(f'Volume Name: ', "blue"), end="")
                    print(ret.spec.template.spec.volumes[i].name)
                    print(colored(f'name (config map name): ', "yellow"), end="")
                    print(ret.spec.template.spec.volumes[i].config_map.name)
                    print(colored(f'default_mode: ', "yellow"), end="")
                    pprint.pprint(ret.spec.template.spec.volumes[i].config_map.default_mode)
                    print(colored(f'items: ', "yellow"), end="")
                    pprint.pprint(ret.spec.template.spec.volumes[i].config_map.items)
                    print(colored(f'optional: ', "yellow"), end="")
                    pprint.pprint(ret.spec.template.spec.volumes[i].config_map.optional)
                    print('\n')
                if ret.spec.template.spec.volumes[i].secret:
                    print(colored(f'Volume Name: ', "blue"), end="")
                    print(ret.spec.template.spec.volumes[i].name)
                    print(colored(f'secret_name: ', "yellow"), end="")
                    pprint.pprint(ret.spec.template.spec.volumes[i].secret.secret_name)
                    print(colored(f'default_mode: ', "yellow"), end="")
                    print(ret.spec.template.spec.volumes[i].secret.default_mode)
                    print(colored(f'items: ', "yellow"), end="")
                    pprint.pprint(ret.spec.template.spec.volumes[i].secret.items)
                    print(colored(f'optional: ', "yellow"), end="")
                    pprint.pprint(ret.spec.template.spec.volumes[i].secret.optional)
        else:
            print(colored(f"Container Volumes ", "red"))
        print('\n')
        print(
            '------------------------------------------------------------------------------------------------------------------------')
        print(colored(f'Container Volume Mounts: \n', "yellow"))
        for i in range(len(ret.spec.template.spec.containers)):
            if ret.spec.template.spec.containers[i].volume_mounts:
                for v in range(len(ret.spec.template.spec.containers[i].volume_mounts)):
                    print(colored(f'Container Name:: ', "blue"), end="")
                    print(ret.spec.template.spec.containers[i].name)
                    print(colored(f'Volume Mount Name: ', "blue"), end="")
                    pprint.pprint(ret.spec.template.spec.containers[i].volume_mounts[v].name)
                    print(colored(f'mount_path: ', "yellow"), end="")
                    print(ret.spec.template.spec.containers[i].volume_mounts[v].mount_path)

                    print(colored(f'read_only: ', "yellow"), end="")
                    print(ret.spec.template.spec.containers[i].volume_mounts[v].read_only)

                    print(colored(f'sub_path: ', "yellow"), end="")
                    print(ret.spec.template.spec.containers[i].volume_mounts[v].sub_path)

                    print(colored(f'sub_path_expr: ', "yellow"), end="")
                    print(ret.spec.template.spec.containers[i].volume_mounts[v].sub_path_expr)

                    print(colored(f'mount_propagation: ', "yellow"), end="")
                    print(ret.spec.template.spec.containers[i].volume_mounts[v].mount_propagation)
                    print('\n')
            else:
                print(colored(f"Container mounts for {ret.spec.template.spec.containers[i].name} not found ", "red"))


        print(
            '------------------------------------------------------------------------------------------------------------------------')
    except client.exceptions.ApiException:
        print(colored(f"Deployment '{args.deployment_name}' not found ", "red"))


def deployment_info_ports(kubeconfig, args):
    config.load_kube_config(config_file=kubeconfig)

    v1 = client.AppsV1Api()
    print(colored(f"Getting information about {args.deployment_name} Ports...\n", 'green'))
    try:
        ret = v1.read_namespaced_deployment(namespace=args.namespace, name=args.deployment_name)
        for i in range(len(ret.spec.template.spec.containers)):
            print(colored(f'{ret.spec.template.spec.containers[i].name} Container Ports: \n', "yellow"))
            for p in range(len(ret.spec.template.spec.containers[i].ports)):
                print(colored(f'name: ', "blue"), end="")
                print(ret.spec.template.spec.containers[i].ports[p].name)

                print(colored(f'container_port: ', "blue"), end="")
                print(ret.spec.template.spec.containers[i].ports[p].container_port)

                print(colored(f'protocol: ', "blue"), end="")
                print(ret.spec.template.spec.containers[i].ports[p].protocol)
                print('\n')


            print(
                '------------------------------------------------------------------------------------------------------------------------')
    except client.exceptions.ApiException:
        print(colored(f"Deployment '{args.deployment_name}' not found ", "red"))


def find_service(kubeconfig, args):
    print(colored(f"Getting information about {args.deployment_name} Service...\n", 'green'))
    config.load_kube_config(config_file=kubeconfig)
    found = False
    v1 = client.CoreV1Api()
    ret = v1.list_namespaced_service(namespace=args.namespace)
    for svc in ret.items:
        if svc.spec.selector:
            if re.search(args.deployment_name, svc.metadata.name):
                print(colored(f'Service Name: ', "yellow"), end="")
                print(svc.metadata.name)
                print(
                    '------------------------------------------------------------------------------------------------------------------------')
                print(colored('Service Ports: \n', "yellow"))
                for p in range(len(svc.spec.ports)):
                    print(colored(f'name: ', "blue"), end="")
                    print(svc.spec.ports[p].name)

                    print(colored(f'target_port: ', "blue"), end="")
                    print(svc.spec.ports[p].target_port)

                    print(colored(f'protocol: ', "blue"), end="")
                    print(svc.spec.ports[p].protocol)

                    if svc.spec.ports[p].node_port:
                        print(colored(f'node_port: ', "blue"), end="")
                        print(svc.spec.ports[p].node_port)
                    print('\n')
                print(
                    '------------------------------------------------------------------------------------------------------------------------')
                print(colored('Selector: \n', "yellow"))
                for k, v in svc.spec.selector.items():
                    print(f'{k}: {v}')
                print(
                    '------------------------------------------------------------------------------------------------------------------------')
                deployment_basic_info(kubeconfig, args)

                found = True
    if not found:
        print(colored(f'Service Not Found', "red"))


def crd_searcher(kubeconfig, args):
    config.load_kube_config(config_file=kubeconfig)

    v1 = client.CustomObjectsApi().list_cluster_custom_object(group="networking.istio.io", version="v1alpha3",
                                                              plural='serviceentries')
    print(colored(f"Getting information about {args.deployment_name}...\n", 'green'))
    try:
        pprint.pprint(v1)
    except client.exceptions.ApiException:
        print(colored(f"Deployment '{args.deployment_name}' not found ", "red"))


def switch(kubeconfig, args):
    for item in args.select:
        if item == 'volumes':
            deployment_info_volumes(kubeconfig, args)
        elif item == 'ports':
            deployment_info_ports(kubeconfig, args)
        elif item == 'service':
            find_service(kubeconfig, args)
        elif item == 'resources':
            deployment_info_resources(kubeconfig, args)
        elif item == 'basic':
            deployment_basic_info(kubeconfig, args)
        elif item == 'affinity':
            deployment_affinity_info(kubeconfig, args)
        elif item == 'hpa':
            deployment_info_hpa(kubeconfig, args)
