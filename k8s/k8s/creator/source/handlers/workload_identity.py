import time
import kopf

import common

import core

logger = common.Logger(__name__)

@kopf.on.resume('workloadidentityconfigs', group="test.com")
@kopf.on.create('workloadidentityconfigs', group="test.com")
def create_fn(spec, name, namespace, logger, **kwargs):
    template = core.config.WorkloadIdentity(
        spec=spec,
        namespace=namespace
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Starting Handler: onCreate')

    core.validator.Permission.validate(
        permissions = template.permissions
    )

    gcpClient = common.GCPClient()

    if not gcpClient.service_account_exist(template = template):
        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Creating new service account')
        gcpClient.service_account_create(
            template=template
        )

        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Waiting for service account to be created')
        gcpClient.service_account_ensure(
            template=template,
            state = True
        )

        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Attaching workload identity config to service account')
        gcpClient.service_account_workload_identity_set(
            template = template
        )

    if not gcpClient.service_account_validate_ownership(template=template):
        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Skipping, we found service account created not by us')

    if len(template.bucket_names) > 0:
        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Updating grant policies for buckets: {template.bucket_names}')
        gcpClient.bucket_policy_allow_access(
            template=template,
            bucket_names=template.bucket_names,
        )
    else:
        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - No grant policies for buckets to update')

    if len(template.permissions) > 0:
        policy = gcpClient.project_iam_policy_get(
            template=template
        )

        if not gcpClient.project_iam_policy_exist(
            template=template,
            permissions=template.permissions,
            policy=policy,
        ):
            logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Starting to add IAM roles: {template.permissions}')
            gcpClient.project_iam_policy_modify(
                template=template,
                permissions=template.permissions,
                policy=policy,
            )

            gcpClient.project_iam_policy_set(
                template=template,
                policy=policy
            )

            time.sleep(5)
        else:
            logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - All IAM roles already exist: {template.permissions}')
    else:
        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - No IAM permissions to update')

    if len(template.bigquery.datasets) > 0:
        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Updating grant policies for BigQuery datasets: {template.bigquery.datasets}')
        gcpClient.dataset_grant_access(
            template=template,
            datasets = template.bigquery.datasets
        )
    else:
        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - No grant policies for BigQuery datasets to update')

@kopf.on.delete('workloadidentityconfigs', group="test.com")
def delete_fn(spec, name, namespace, logger, **kwargs):
    template = core.config.WorkloadIdentity(
        spec=spec,
        namespace=namespace
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Starting Handler: onDelete')

    gcpClient = common.GCPClient()

    if template.lifecycle.reclaimPolicy == 'Retain':
        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - All resources will be kept after CR removal due to retain lifecycle policy set on resource')
        return True

    if not gcpClient.service_account_exist(template = template):
        logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Skipping, service account already deleted')
        return True

    if not gcpClient.service_account_validate_ownership(template=template):
        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Skipping, we found service account created not by us')

    policy = gcpClient.project_iam_policy_get(
        template=template
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Removing IAM permissions: {template.permissions}')
    gcpClient.project_iam_remove_role(
        template=template,
        policy=policy,
        permissions=template.permissions
    )

    gcpClient.project_iam_policy_set(
        template=template,
        policy=policy
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Removing grant policies for buckets: {template.bucket_names}')
    gcpClient.bucket_policy_remove_iam_member(
        template=template,
        bucket_names=template.bucket_names
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Delete service account')
    gcpClient.service_account_delete(
        template=template
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Waiting for service account to be deleted')
    gcpClient.service_account_ensure(
        template=template,
        state = False
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Revoking permissions for datasets {template.bigquery.datasets}')
    gcpClient.dataset_revoke_access(
        template=template,
        datasets=template.bigquery.datasets
    )


@kopf.on.update('workloadidentityconfigs', group="test.com", field='spec.permissions')
def update_permissions_fn(spec, old, new, name, namespace, logger, **kwargs):
    template = core.config.WorkloadIdentity(
        spec=spec,
        namespace=namespace
    )

    core.validator.Permission.validate(
        permissions = new
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Starting Handler: onUpdate permissions')

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Current permissions set: {old}, new permissions set: ${new}')

    updated_permissions = list(set(old).difference(new))
    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Change permissions set: {updated_permissions}')

    gcpClient = common.GCPClient()

    if not gcpClient.service_account_exist(template = template):
        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Missing service account while updating its permissions')

    if not gcpClient.service_account_validate_ownership(template=template):
        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Skipping, we found service account created not by us')

    policy = gcpClient.project_iam_policy_get(
        template=template
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Starting to modify IAM roles: {new}')
    gcpClient.project_iam_policy_modify(
        template=template,
        permissions=new,
        policy=policy,
    )

    gcpClient.project_iam_policy_set(
        template=template,
        policy=policy
    )

@kopf.on.update('workloadidentityconfigs', group="test.com", field='spec.buckets')
def update_buckets_fn(spec, old, new, name, namespace, logger, **kwargs):
    template = core.config.WorkloadIdentity(
        spec=spec,
        namespace=namespace
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Starting Handler: onUpdate buckets')

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Current buckets set: {old}, new buckets set: ${new}')

    updated_buckets = list(set(old).difference(new))
    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Change permissions set: {updated_buckets}')

    gcpClient = common.GCPClient()

    if not gcpClient.service_account_exist(template = template):
        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Missing service account while updating buckets')

    if not gcpClient.service_account_validate_ownership(template=template):
        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Skipping, we found service account created not by us')

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Removing grant policies for buckets: {updated_buckets}')
    gcpClient.bucket_policy_remove_iam_member(
        template=template,
        bucket_names=updated_buckets
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Updating grant policies for buckets: {new}')
    gcpClient.bucket_policy_allow_access(
        template=template,
        bucket_names=new,
   )

@kopf.on.update('workloadidentityconfigs', group="test.com", field='spec.bigquery.datasets')
def update_datasets_fn(spec, old, new, name, namespace, logger, **kwargs):
    template = core.config.WorkloadIdentity(
        spec=spec,
        namespace=namespace
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Starting Handler: onUpdate datasets')

    if old is None:
        old = []

    if new is None:
        new = []

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Current datasets set: {old}, new datasets set: ${new}')

    revoked_datasets = list(set(old).difference(new))
    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Revoke permissions set: {revoked_datasets}')

    gcpClient = common.GCPClient()

    if not gcpClient.service_account_exist(template = template):
        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Missing service account while updating bigquery datasets')

    if not gcpClient.service_account_validate_ownership(template=template):
        raise common.Exception(logger, f'Service Account: {template.gcp_service_account_name}{template.email} - Skipping, we found service account created not by us')

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Revoke permissions for: {revoked_datasets}')
    gcpClient.dataset_revoke_access(
        template=template,
        datasets=revoked_datasets
    )

    logger.info(f'Service Account: {template.gcp_service_account_name}{template.email} - Updating grant policies for datasets: {new}')
    gcpClient.dataset_grant_access(
        template=template,
        datasets=new
    )