
import common

logger = common.Logger(__name__)

class Lifecycle:
    def __init__(self, lifecycle):
        if lifecycle is None:
            raise common.Exception(logger, f'Service Account: {self.gcp_service_account_name}{self.email} - Lifecycle block is empty')

        self.__reclaimPolicy = lifecycle.get('reclaimPolicy')
        if self.__reclaimPolicy is None:
            raise common.Exception(logger, f"Service Account: {self.gcp_service_account_name}{self.email} - reclaimPolicy must be set in lifecycle")
        if self.__reclaimPolicy not in ['Delete', 'Retain']:
            raise common.Exception(logger, f"Service Account: {self.gcp_service_account_name}{self.email} - reclaimPolicy must be Delete on Retain")

    @property
    def reclaimPolicy(self):
        return self.__reclaimPolicy

class BigQuery:
    def __init__(self, bigquery):
        if bigquery is None:
            logger.info(f'Service Account: {self.gcp_service_account_name}{self.email} - BigQuery is missing in custom resource, setting to empty')
            self.__datasets = []
            return

        self.__datasets = bigquery.get('datasets')
        if self.__datasets is None:
            raise common.Exception(logger, f"Service Account: {self.gcp_service_account_name}{self.email} - Datasets must be set in BigQuery")

        if not isinstance(self.__datasets, list):
            raise common.Exception(logger, f"Service Account: {self.gcp_service_account_name}{self.email} - Datasets must be of list format")

    @property
    def datasets(self):
        return self.__datasets

class WorkloadIdentity:
    def __init__(self, spec, namespace):
        self.__gcp_service_account_name = spec.get('gcpServiceAccountName')
        if self.__gcp_service_account_name is None:
            raise common.Exception(logger, f"Service Account: Unknown - gcpServiceAccountName must be set. Got {self.__gcp_service_account_name!r}.")

        self.__k8s_service_accountName = spec.get('k8sServiceAccountName')
        if self.__k8s_service_accountName is None:
            raise common.Exception(logger, f"Service Account: {self.gcp_service_account_name}{self.email} - k8sServiceAccountName must be set. Got {self.__k8s_service_accountName!r}.")

        self.__project_id = spec.get('projectId')
        if self.__project_id is None:
            raise common.Exception(logger, f"Service Account: {self.gcp_service_account_name}{self.email} - project_id must be set. Got {self.__project_id!r}.")

        self.__namespace = namespace
        if self.__namespace is None:
            raise common.Exception(logger, f"Service Account: {self.gcp_service_account_name}{self.email} - namespace must be set. Got {self.__namespace!r}.")

        self.__permissions = spec.get("permissions")
        if self.__permissions is None:
            logger.info(f'Service Account: {self.gcp_service_account_name}{self.email} - Permissions is missing in custom resource, setting to empty')
            self.__permissions = []

        self.__bucket_names = spec.get('buckets')
        if self.__bucket_names is None:
            logger.info(f'Service Account: {self.gcp_service_account_name}{self.email} - Buckets is missing in custom resource, setting to empty')
            self.__bucket_names = []

        self.__bigquery = BigQuery(
            bigquery = spec.get('bigquery')
        )

        self.__lifecycle = Lifecycle(
            lifecycle = spec.get('lifecycle')
        )

    @property
    def project_id(self):
        return self.__project_id

    @property
    def gcp_service_account_name(self):
        return self.__gcp_service_account_name

    @property
    def namespace(self):
        return self.__namespace

    @property
    def k8s_service_account_name(self):
        return self.__k8s_service_accountName

    @property
    def permissions(self):
        return self.__permissions

    @property
    def bucket_names(self):
        return self.__bucket_names

    @property
    def email(self):
        return f"@{self.project_id}.iam.gserviceaccount.com"

    @property
    def member(self):
        return f"serviceAccount:{self.gcp_service_account_name}{self.email}"

    @property
    def bigquery(self):
        return self.__bigquery

    @property
    def lifecycle(self):
        return self.__lifecycle