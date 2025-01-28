# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
import json
from botocore.exceptions import ClientError

region_name = "us-east-1"
secret_name = "arn:aws:secretsmanager:us-east-1:376778049323:secret:digitalcorpora_stats_dbreader-XkbHox"


def get_secret():
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    print("response=",json.dumps(get_secret_value_response,indent=4,default=str))
    return json.loads(get_secret_value_response['SecretString'])

if __name__=="__main__":
    secret = get_secret()
    print("successfully got secret")
