import re


class Funcs:

    def __init__(self, session, cluster_name):
        self.session = session
        self.cluster_name = cluster_name

    def get_secrets_by_prefix(self, prefix_list):
        secrets_list = []
        client = self.session.client('secretsmanager')

        for i in range(len(prefix_list)):
            response = client.list_secrets(
                MaxResults=100,
                Filters=[
                    {
                        'Key': 'name',
                        'Values': [
                            prefix_list[i],
                        ]
                    },
                ],
            )
            for s in response['SecretList']:
                secrets_list.append(s['Name'])
            try:
                next_token = response['NextToken']
            except KeyError:
                print(f"No more secrets for {prefix_list[i]}")
                next_token = None
                continue
            while next_token is not None:
                response = client.list_secrets(
                    MaxResults=100,
                    NextToken=next_token,
                    Filters=[
                        {
                            'Key': 'name',
                            'Values': [
                                prefix_list[i],
                            ]
                        },
                    ],
                )
                for s in response['SecretList']:
                    secrets_list.append(s['Name'])
                try:
                    next_token = response['NextToken']
                except KeyError:
                    print(f"No more secrets for {prefix_list[i]}")
                    next_token = None
                    continue

        return secrets_list

    def get_secrets_values_by_prefix(self, secrets_list):
        client = self.session.client('secretsmanager')
        for i in range(len(secrets_list)):
            response = client.get_secret_value(
                SecretId=secrets_list[i]
            )
            # for c in secrets_list[i]:
            #     if c == "/":
            #         sub = secrets_list[i].replace("/", "_")
            # for c in sub:
            #     if c == "-":
            #         sub = sub.replace("-", "_")

            sub = Funcs.filter_name(secret_name=secrets_list[i], char='/')
            sub = Funcs.filter_name(secret_name=sub, char="-")
            sub = Funcs.filter_name(secret_name=sub, char=".")
            sub = Funcs.filter_name(secret_name=sub, char="+")
            sub = Funcs.filter_name(secret_name=sub, char="=")
            sub = Funcs.filter_name(secret_name=sub, char="@")

            with open("secrets", "a") as f:
                f.write("export %s='%s'\n" % (
                    sub,
                    response['SecretString']
                ))

        f.close()

    def filter_name(secret_name, char):

        for c in secret_name:
            if c == char:
                print(f'Replacing "{char}" in {secret_name}')
                secret_name = secret_name.replace(f"{char}", "_")
            else:
                continue
        return secret_name


if __name__ == '__main__':
    Funcs()
