import boto3


class Session:
    def __init__(self, aws_profile, aws_region, aws_access_key_id, aws_secret_access_key, aws_session_token):
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token

    def start_session(self):
        if self.aws_profile is not None:
            session = boto3.Session(
                profile_name=self.aws_profile,
                region_name=self.aws_region
            )
        else:
            session = boto3.Session(
                region_name = self.aws_region,
                aws_access_key_id = self.aws_access_key_id,
                aws_secret_access_key = self.aws_secret_access_key,
                aws_session_token = self.aws_session_token
            )

        return session
