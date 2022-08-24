import os

import re

import parser.parser as parser
import initiator.session as ses
import aws_module.functions as aws


def main():
    aws_profile = os.environ.get('AWS_PROFILE')
    aws_region = os.environ.get('AWS_REGION')
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.environ.get('AWS_SESSION_TOKEN')

    session = ses.Session(
        aws_profile=aws_profile,
        aws_region=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token
    )

    session = session.start_session()

    parse = parser.Parser()
    args = parse.get()

    for i in vars(args).values():
        prefix_list = i.split(',')

    aws_client = aws.Funcs(session, prefix_list)

    secrets = aws_client.get_secrets_by_prefix(prefix_list)
    # print(secrets)
    aws_client.get_secrets_values_by_prefix(secrets)


if __name__ == '__main__':
    main()
