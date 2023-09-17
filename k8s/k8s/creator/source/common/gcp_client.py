import time
from google.oauth2 import service_account  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.cloud import storage
from google.cloud import bigquery
from google.cloud.bigquery.enums import EntityTypes
from google.api_core import exceptions
import kopf

import common

logger = common.Logger(__name__)

class GCPClient:
    def __init__(self):
        self.__iamClient = googleapiclient.discovery.build("iam", "v1")
        self.__cloudResourceManagerClient = googleapiclient.discovery.build("cloudresourcemanager", "v1")
        self.__storageClient = storage.Client()
        self.__bigqueryClient = bigquery.Client()

    def service_account_exist(self, template):
        try:
            request = self.__iamClient.projects().serviceAccounts().get(
                name=f'projects/{template.project_id}/serviceAccounts/{template.gcp_service_account_name}{template.email}'
            ).execute()

            if not request or 'name' not in request:
                return False

            return True
        except Exception as e:
            return False

    def service_account_validate_ownership(self, template):
        request = self.__iamClient.projects().serviceAccounts().get(
            name=f'projects/{template.project_id}/serviceAccounts/{template.gcp_service_account_name}{template.email}'
        ).execute()

        if not request or 'name' not in request or 'displayName' not in request:
            raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Invalid service account')

        display_name = f"Created by Operator for {template.gcp_service_account_name}"
        if request['displayName'] != display_name:
            return False

        return True

    def service_account_get(self, template):
        request = self.__iamClient.projects().serviceAccounts().get(
            name=f'projects/{template.project_id}/serviceAccounts/{template.gcp_service_account_name}{template.email}'
        ).execute()

        if not request or 'name' not in request:
            raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Invalid service account')

        return {
            'name': request['name'],
            'projectId': request['projectId'],
            'email': request['email'],
            'displayName': request['displayName']
        }

    def service_account_create(self, template):
        display_name = f"Created by Operator for {template.gcp_service_account_name}"
        service_account = self.__iamClient.projects().serviceAccounts().create(
            name="projects/" + template.project_id,
            body={
                "accountId": template.gcp_service_account_name,
                "serviceAccount": {"displayName": f"{display_name}"}
            }).execute()

        return service_account

    def service_account_delete(self, template):
        self.__iamClient.projects().serviceAccounts().delete(
            name=f"projects/-/serviceAccounts/{template.gcp_service_account_name}{template.email}"
        ).execute()

    def service_account_ensure(self, template, state):
        count = 5
        while count > 0:
            flag = self.service_account_exist(template = template)

            if flag == state:
                logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Reached for state: {state}')
                return True

            logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Waiting for state: {state}')
            time.sleep(3)
            count = count - 1

        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Unable to ensure state: {state}')

    def service_account_workload_identity_set(self, template):
        service_account_resource = f"projects/{template.project_id}/serviceAccounts/{template.gcp_service_account_name}{template.email}"
        workload_identity = f"serviceAccount:{template.project_id}.svc.id.goog[{template.namespace}/{template.k8s_service_account_name}]"

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

    def project_iam_policy_get(self, template):
        version = 1

        policy = self.__cloudResourceManagerClient.projects().getIamPolicy(
            resource=template.project_id,
            body={
                "options": {"requestedPolicyVersion": version}
            },
        ).execute()

        return policy

    def project_iam_policy_set(self, template, policy):
        policy = self.__cloudResourceManagerClient.projects().setIamPolicy(
            resource=template.project_id,
            body={"policy": policy}
        ).execute()

        return policy

    def project_iam_policy_exist(self, template, permissions, policy):
        for role in permissions:
            found = False
            for binding in policy['bindings']:
                if binding['role'] == role and template.member in binding['members']:
                    found = True

            if not found:
                return False

        return True

    def project_iam_policy_modify(self, template, permissions, policy):
        for binding in policy['bindings']:
            if template.member in binding['members']:
                if not binding['role'] in permissions:
                    logger.info(f"Service Account: {template.gcp_service_account_name}{template.email} - IAM role: {role} removed.")
                    binding['members'].remove(template.member)

        for role in permissions:
            for binding in policy['bindings']:
                if binding['role'] == role and template.member not in binding['members']:
                    logger.info(f"Service Account: {template.gcp_service_account_name}{template.email} - IAM role: {role} added.")
                    binding['members'].append(template.member)

        return policy

    def project_iam_remove_role(self, template, policy, permissions):
        for binding in policy["bindings"]:
            for role in permissions:
                if binding['role'] == role and template.member in binding['members']:
                    binding['members'].remove(template.member)
                    logger.info(f"Service Account: {template.gcp_service_account_name}{template.email} - IAM role: {role} removed.")

    def bucket_policy_allow_access(self, template, bucket_names):
        if not bucket_names:
            logger.info(f"Service Account: {template.gcp_service_account_name}{template.email} - No buckets to configure")
            return

        role = "roles/storage.admin"

        for bucket_name in bucket_names:
            if not self.__bucket_exist(
                template=template,
                bucket_name=bucket_name
            ):
                logger.warning(f'Service Account: {template.gcp_service_account_name}{template.email}, Bucket: {bucket_name} - Skipping, bucket is missing')
                continue

            if self.__bucket_policy_exist(
                template=template,
                role=role,
                bucket_name=bucket_name
            ):
                logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Bucket: {bucket_name} - Skipping, already have access')
            else:
                logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Bucket: {bucket_name} - Adding access.')
                self.__bucket_policy_set(
                    template=template,
                    role=role,
                    bucket_name=bucket_name
                )

        time.sleep(3)

    def bucket_policy_remove_iam_member(self, template, bucket_names):
        for bucket_name in bucket_names:
            if not self.__bucket_exist(
                template=template,
                bucket_name=bucket_name
            ):
                logger.warning(f'Service Account: {template.gcp_service_account_name}{template.email}, Bucket: {bucket_name} - Skipping, bucket is missing')
                continue

            logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Bucket: {bucket_name} - Removing access from {template.member}')
            self.__bucket_policy_remove(
                template=template,
                bucket_name=bucket_name
            )

    def __bucket_exist(self, template, bucket_name):
        try:
            bucket = self.__storageClient.get_bucket(bucket_name)
        except exceptions.NotFound:
            return False

        return True

    def __bucket_policy_exist(self, template, role, bucket_name):
        gcp_bucket = self.__storageClient.bucket(bucket_name)
        policy = gcp_bucket.get_iam_policy(
            requested_policy_version=3
        )
        policy.version = 3

        for binding in policy.bindings:
            if binding['role'] == role and template.member in binding['members']:
                return True

        return False


    def __bucket_policy_set(self, template, role, bucket_name):
        gcp_bucket = self.__storageClient.bucket(bucket_name)
        policy = gcp_bucket.get_iam_policy(
            requested_policy_version=3
        )

        policy.version = 3

        policy.bindings.append(
            {
                "role": role,
                "members": [template.member],
                "condition": {
                    "title": f"{bucket_name}-access",
                    "description": f"Access to {bucket_name} bucket",
                    "expression": f"resource.name.startsWith(\"projects/_/buckets/{bucket_name}\")",
                },
            }
        )

        gcp_bucket.set_iam_policy(policy)

        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Bucket: {bucket_name} - Granted access to bucket.')
        time.sleep(2)

    def __bucket_policy_remove(self, template, bucket_name):
        bucket = self.__storageClient.bucket(bucket_name)

        policy = bucket.get_iam_policy(
            requested_policy_version=3
        )

        for binding in policy.bindings:
            if "storage" in binding["role"] and binding.get("condition"):
                binding["members"].discard(template.member)

        bucket.set_iam_policy(policy)

    def dataset_grant_access(self, template, datasets):
        if not datasets:
            logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - No datasets to configure.')
            return

        for dataset_name in datasets:
            if not self.__dataset_exist(
                template=template,
                dataset_name=dataset_name
            ):
                logger.warning(f'Service Account: {template.gcp_service_account_name}{template.email}, Dataset: {dataset_name} - Skipping, dataset not found')
                continue

            if self.__dataset_policy_exist(
                template=template,
                dataset_name=dataset_name
            ):
                logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Dataset: {dataset_name} - Skipping, already granted access.')
            else:
                logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Dataset: {dataset_name} - Granting access to dataset.')
                self.__dataset_policy_set(
                    template=template,
                    dataset_name=dataset_name
                )

    def __dataset_exist(self, template, dataset_name):
        dataset_ref = self.__bigqueryClient.dataset(
            dataset_name,
            project=template.project_id
        )

        try:
            dataset = self.__bigqueryClient.get_dataset(dataset_ref)
        except exceptions.NotFound:
            return False

        return True

    def __dataset_policy_exist(self, template, dataset_name):
        entity_type = EntityTypes.USER_BY_EMAIL

        dataset_ref = self.__bigqueryClient.dataset(
            dataset_name,
            project=template.project_id
        )

        dataset = self.__bigqueryClient.get_dataset(dataset_ref)
        entries = list(dataset.access_entries)
        for entry in entries:
            if entry.role == "OWNER" and entry.entity_type == entity_type and entry.entity_id == f"{template.gcp_service_account_name}{template.email}":
                return True

        return False

    def __dataset_policy_set(self, template, dataset_name):
        entity_type = EntityTypes.USER_BY_EMAIL

        dataset = self.__bigqueryClient.get_dataset(dataset_name)
        entries = list(dataset.access_entries)
        entries.append(
            bigquery.AccessEntry(
                role="OWNER",
                entity_type=entity_type,
                entity_id=f"{template.gcp_service_account_name}{template.email}",
            )
        )
        dataset.access_entries = entries
        dataset = self.__bigqueryClient.update_dataset(dataset, ["access_entries"])

    def dataset_revoke_access(self, template, datasets): # should send the diff between old and new
        for dataset_name in datasets:
            if not self.__dataset_exist(
                template=template,
                dataset_name=dataset_name
            ):
                logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Dataset: {dataset_name} - Skipping, dataset not found')
                continue

            if self.__dataset_policy_exist(
                template=template,
                dataset_name=dataset_name
            ):
                logger.info(f"Dataset {dataset_name} removing record.")
                logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Dataset: {dataset_name} - Removing access to dataset.')
                self.__dataset_policy_remove(
                    template=template,
                    dataset_name=dataset_name
                )
            else:
                logger.info(f'Service Account: {template.gcp_service_account_name}{template.email}, Dataset: {dataset_name} - Skipping, already removed access to dataset.')

    def __dataset_policy_remove(self, template, dataset_name):
        filtered_entries = []

        dataset = self.__bigqueryClient.get_dataset(dataset_name)  # Make an API request.
        entries = list(dataset.access_entries)

        for entry in dataset.access_entries:
            if entry.entity_id != f"{template.gcp_service_account_name}{template.email}":
                filtered_entries.append(entry)

        dataset.access_entries = filtered_entries
        dataset = self.__bigqueryClient.update_dataset(dataset, ["access_entries"])