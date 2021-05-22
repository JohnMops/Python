import boto3
import os

class Session:

    def __init__(self, profile, region, aws_access_key_id, aws_secret_access_key):
        self.profile = profile
        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def start_session(self):
        if self.profile is not 'None':
            session = boto3.session.Session(profile_name=self.profile, region_name=self.region)
        else:
            session = boto3.session.Session(region_name=self.region,
                                            aws_access_key_id=self.aws_access_key_id,
                                            aws_secret_access_key=self.aws_secret_access_key)
        return session


if __name__ == '__main__':
    Session()

