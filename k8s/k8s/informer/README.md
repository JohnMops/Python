pip3 install -r requirements.txt


python3 main.py -h For help

python3 main.py --deployment-name <deploy_name> --namespace <namespace_name> For all information

python3 main.py --deployment-name <deploy_name> --namespace <namespace_name> --select hpa For specific component info

python3 main.py --deployment-name <deploy_name> --namespace <namespace_name> --select hpa service volumes For multiple components