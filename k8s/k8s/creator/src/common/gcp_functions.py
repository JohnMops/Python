import logging
import time
from google.oauth2 import service_account  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.cloud import storage
import kopf


class GCPClient:
    def __init__(self):
        self.__iamClient = googleapiclient.discovery.build("iam", "v1")
        self.__cloudResourceManagerClient = googleapiclient.discovery.build("cloudresourcemanager", "v1")
        self.__storageClient = storage.Client()

    def check_service_account(self, template):
        try:
            request = self.__iamClient.projects().serviceAccounts().get(
                name=f'projects/{template.project_id}/serviceAccounts/{template.gcp_service_account_name}{template.email}'
            ).execute()
            if request['displayName'] == template.gcp_service_account_name:
                logging.info(f"Service Account: {template.gcp_service_account_name}{template.email} Already exists")
                return True
            else:
                logging.info(f"Service Account: {template.gcp_service_account_name}{template.email} Does Not exists")
                return False
        except Exception as e:
            pass

    def create_service_account(self, template):
        try:
            service_account = self.__iamClient.projects().serviceAccounts().create(
                name="projects/" + template.project_id,
                body={
                    "accountId": template.gcp_service_account_name,
                    "serviceAccount": {"displayName": template.gcp_service_account_name}
                }).execute()

            logging.info("Created service account: " + service_account["email"])
            return service_account
        except Exception as e:
            logging.error(e)

    def delete_service_account(self, template):
        try:
            self.__iamClient.projects().serviceAccounts().delete(
                name=f"projects/-/serviceAccounts/{template.gcp_service_account_name}{template.email}"
            ).execute()

            logging.info(f"Deleted service account: {template.gcp_service_account_name}{template.email}")
        except Exception as e:
            logging.error(e)

    def get_project_iam_policy(self, template):
        version = 1

        policy = self.__cloudResourceManagerClient.projects().getIamPolicy(
            resource=template.project_id,
            body={
                "options": {"requestedPolicyVersion": version}
            },
        ).execute()

        return policy

    def set_workload_identity(self, template):
        service_account_resource = f"projects/{template.project_id}/serviceAccounts/{template.gcp_service_account_name}{template.email}"
        workload_identity = f"serviceAccount:{template.project_id}.svc.id.goog[{template.namespace}/{template.gcp_service_account_name}]"

        # logging.info(policy)

        set_iam_policy_request_body = {
            "policy": {
                "bindings": [
                    {
                        "role": "roles/iam.workloadIdentityUser",
                        "members": [workload_identity]
                    },
                    {
                        "role": "roles/iam.serviceAccountTokenCreator",
                        "members": [template.member]
                    }
                ]
            }
        }

        request = self.__iamClient.projects().serviceAccounts().setIamPolicy(
            resource=service_account_resource,
            body=set_iam_policy_request_body
        ).execute()

        logging.info(f"Workload Identity policy bound to {template.gcp_service_account_name}{template.email}")

    def modify_policy_add_role(self, template, permissions, policy, bucket_names):

        if bucket_names:
            self.set_bucket_policy(
                template=template,
                policy=policy,
                role="roles/storage.admin",
                bucket_names=bucket_names
            )
            time.sleep(3)
        try:
            if permissions:
                for role in permissions:
                    binding = {
                        "role": role,
                        "members": [template.member]
                    }
                    policy["bindings"].append(binding)
                    logging.info(f"'{role}' will remain on {template.member}")
                return policy
        except Exception as e:
            logging.error(e)

    def remove_bucket_iam_member(self, template, bucket_names):
        logging.info(f"Buckets {bucket_names} will be stripped from permissions for {template.member}")
        try:
            for i in range(len(bucket_names)):
                bucket = self.__storageClient.bucket(bucket_names[i])

                policy = bucket.get_iam_policy(
                    requested_policy_version=3
                )

                for binding in policy.bindings:
                    if "storage" in binding["role"] and binding.get("condition"):
                        binding["members"].discard(template.member)

                bucket.set_iam_policy(policy)

                logging.info(f"Removed {template.member} with role 'roles/storage.admin' from {bucket_names[i]}.")
        except:
            raise kopf.TemporaryError(f"Another operation in performed on bucket: {bucket_names[i]}. Operator will retry", delay=10)

    def set_policy(self, template, policy):
        try:
            policy = self.__cloudResourceManagerClient.projects().setIamPolicy(
                resource=template.project_id,
                body={"policy": policy}
            ).execute()
        except:
            raise kopf.TemporaryError(f"Another Set Policy operation is performed: Operator will retry", delay=10)

        return policy

    def set_bucket_policy(self, template, policy, role, bucket_names):

        try:
            for i in range(len(bucket_names)):
                gcp_bucket = self.__storageClient.bucket(bucket_names[i])
                policy = gcp_bucket.get_iam_policy(
                    requested_policy_version=3
                )

                policy.version = 3

                policy.bindings.append(
                    {
                        "role": role,
                        "members": [template.member],
                        "condition": {
                            "title": f"{bucket_names[i]}-access",
                            "description": f"Access to {bucket_names[i]} bucket",
                            "expression": f"resource.name.startsWith(\"projects/_/buckets/{bucket_names[i]}\")",
                        },
                    }
                )

                gcp_bucket.set_iam_policy(policy)

                logging.info(f"{template.member} is now a {role} on {bucket_names[i]} bucket")
        except:
            raise kopf.TemporaryError(f"Another operation in performed on bucket: {bucket_names[i]}. Operator will retry", delay=10)
    def remove_role_from_member(self, template, policy, permissions):
        try:
            for binding in policy["bindings"]:
                for role in permissions:
                    if binding['role'] == role and template.member in binding['members']:
                        binding['members'].remove(template.member)
                        logging.info(f"'{role}' will be Removed on {template.member}")
        except:
            raise kopf.TemporaryError(f"Another Role Removal operatrion is in progress. Operator will retry", delay=10)
