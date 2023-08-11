

import kopf

class GCPTemplateCR:
    def __init__(self, spec):
        self.__project_id = spec.get('projectId')
        if not self.__project_id:
            raise kopf.PermanentError(f"project_id must be set. Got {self.__project_id!r}.")

        self.__gcp_service_account_name = spec.get('gcpServiceAccountName')
        if not self.__gcp_service_account_name:
            raise kopf.PermanentError(f"gcpServiceAccountName must be set. Got {self.__gcp_service_account_name!r}.")

        self.__namespace = spec.get('namespace')
        if not self.__namespace:
            raise kopf.PermanentError(f"namespace must be set. Got {self.__namespace!r}.")

        self.__k8s_service_accountName = spec.get('k8sServiceAccountName')
        if not self.__k8s_service_accountName:
            raise kopf.PermanentError(f"k8sServiceAccountName must be set. Got {self.__k8s_service_accountName!r}.")

        self.__permissions = spec.get("permissions")

        self.__bucket_names = spec.get('buckets')

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