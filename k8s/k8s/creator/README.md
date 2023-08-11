# GCP Service Account Creator as a kubernetes operator


1. Inside the "crds" folder you will find the Custom Resource that this operator 
will look for in your cluster
2. You can create this as a part of the service chart/manually/gitops
3. The values can come from your values.yaml per chart to easily control each service account

# Workflow: 

1. A service account will be created if it does not exist
2. A workload identity will be configured on the service account to connect it to your k8s
3. "permissions" block will add/remove permissions on the fly from your service accound
4. "buckets" block will add "roles/storage.admin" to your service account but only on the bucket
that starts with the bucket name to keep with the least privileged attitude.
5. Removing the "buckets" and "permissions" blocks will leave the service account and it will
remain strapped with the workload identity for you to add permissions to at a later time
6. Removing the Custom Resource will remove all the binds from all policies for this service account
and delete the service account from your project
7. Migrate existing service accounts by changing the display name to match the string:
"Created by Operator for _your service account name_" or by simply deleting them all together.
The operator will take control over the service accounts with the appropriate display name or create new once
if none exist.

### Notes: 
1. The number of workers (threads) this operator opens was limited to 1 to avoid GCP API collisions when creating multiple Custom Resources.
2. The operator itself will need a service account with IAM and Storage admins in your project
3. Your k8s cluster will need a service account for the operator with permissions to get the Custom Resources in all namespaces


