##How to use:

```
pip install -r requirements.txt 
export AWS_REGION=<region>
export CLUSTER_NAME=<cluster_name>

If you want to use profile: 
export AWS_PROFILE=<profile_name>
```

##What information you currently get:

1. Shows the EKS control plane subnets
2. Shows the EKS VPC
3. Shows Private Loadbalancers that are related to your cluster
   - If exists, will show Status, Type, Scheme, Host Name, Hosted Zone
   - Green/Red colors
   - Show LB tags
   - If LB is managed by Istio, will highlight
4. Shows Public Loadbalancers that are related to your cluster
   - If exists, will show Status, Type, Scheme, Host Name, Hosted Zone
   - Green/Red colors
   - Show LB tags 
   - If LB is managed by Istio, will highlight 
5. Checks Public/Private subnets use by you Load Balancers
   - Will check if all the tags are present according to the AWS requirements
   - Will check and highlight if Free IPs are < 500 
   - Will check if the public subnets have a route to IGW 
6. Iterate over your cluster EC2 instances and show the security group attached    
7. Will check the above groups and show all routes that are opened to 0.0.0.0/0
8. Will show all non-cluster related EC2 instances
9. Will check Route53 Zones
   - Will show Zone Type,ID
10. Will perform a DIG test to the zone domain and show which zone is answering the request    




