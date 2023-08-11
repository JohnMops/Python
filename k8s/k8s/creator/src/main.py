import pprint
import time
import kopf
import logging
from datetime import datetime
import logging
from google.oauth2 import service_account  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.cloud import storage

import common


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.execution.max_workers = 1

@kopf.on.resume('gcptemplates', group="creator.com")
@kopf.on.create('gcptemplates', group="creator.com")
def create_fn(spec, name, namespace, logger, **kwargs):
    template = common.GCPTemplateCR(
        spec=spec
    )

    gcpClient = common.GCPClient()
    check_sa = gcpClient.check_service_account(
        template=template
    )
    if not check_sa:
        gcpClient.create_service_account(
            template=template
        )
        time.sleep(3)

    check_sa = gcpClient.check_service_account(
        template=template
    )

    if check_sa:
        gcpClient.set_workload_identity(
            template=template
        )

    if check_sa:
        policy = gcpClient.get_project_iam_policy(
            template=template
        )

        gcpClient.modify_policy_add_role(
            template=template,
            permissions=template.permissions,
            bucket_names=template.bucket_names,
            policy=policy,
        )

        gcpClient.set_policy(
            template=template,
            policy=policy
        )
        time.sleep(3)


@kopf.on.delete('gcptemplates', group="creator.com")
def delete_fn(spec, name, namespace, logger, **kwargs):
    template = common.GCPTemplateCR(
        spec=spec
    )


    gcpClient = common.GCPClient()

    check_sa = gcpClient.check_service_account(
        template=template
    )

    if check_sa:

        policy = gcpClient.get_project_iam_policy(
            template=template
        )

        gcpClient.remove_role_from_member(
            template=template,
            policy=policy,
            permissions=template.permissions
        )

        gcpClient.set_policy(
            template=template,
            policy=policy
        )

        gcpClient.remove_bucket_iam_member(
            template=template,
            bucket_names=template.bucket_names
        )


        gcpClient.delete_service_account(
            template=template
        )

        time.sleep(3)



@kopf.on.update('gcptemplates', group="creator.com", field='spec.permissions')
def update_permissions_fn(spec, old, new, name, namespace, logger, **kwargs):
    logger.info(f"Old: {old}")
    logger.info("--------------------------------")
    logger.info(f"New: {new}")

    updated_permissions = list(set(old).difference(new))

    template = common.GCPTemplateCR(
        spec=spec
    )

    gcpClient = common.GCPClient()

    policy = gcpClient.get_project_iam_policy(
        template=template
    )

    gcpClient.remove_role_from_member(
        template=template,
        policy=policy,
        permissions=updated_permissions
    )

    gcpClient.modify_policy_add_role(
        bucket_names=template.bucket_names,
        template=template,
        permissions=new,
        policy=policy
    )

    gcpClient.set_policy(
        template=template,
        policy=policy
    )


@kopf.on.update('gcptemplates', group="creator.com", field='spec.buckets')
def update_buckets_fn(spec, old, new, name, namespace, logger, **kwargs):
    logger.info(f"Old: {old}")
    logger.info("--------------------------------")
    logger.info(f"New: {new}")

    template = common.GCPTemplateCR(
        spec=spec
    )
    gcpClient = common.GCPClient()
    if not old:
        return

    updated_buckets = list(set(old).difference(new))
    logging.info(f"Removing permissins from {updated_buckets}")



    policy = gcpClient.get_project_iam_policy(
        template=template
    )

    gcpClient.remove_bucket_iam_member(
        template=template,
        bucket_names=updated_buckets
    )
    gcpClient.modify_policy_add_role(
        template=template,
        bucket_names=new,
        policy=policy,
        permissions=template.permissions
    )

