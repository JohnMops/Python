from kubernetes import client, config


class Kube():
    cfg = config.load_kube_config()

    # config.incluster_config()

    def __init__(self):
        self.core_api = client.CoreV1Api()
        self.apis_api = client.AppsV1Api()

    def get_namespaces(self):
        response = self.core_api.list_namespace()
        namespace_list = []
        for n in response.items:
            namespace_list.append(f"{n.metadata.name}")
        return namespace_list


if __name__ == '__main__':
    Kube()
