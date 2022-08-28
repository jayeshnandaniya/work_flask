"""
Get credentials from secret manager.
Right now that's AWS Secrets Manager.

By default it will use the [default] profile
in your ~/.aws/credentials but you can use
environment variables to overwrite this.

More info here:
https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html
"""

import json
import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def get_creds(secret_name):
    """
    Get credentials from AWS Secrets Manager
    The secret_full_name naming scheme is by convention.
    Returns a dictionary of key/value pairs from the secret body.
    """
    project = os.environ['PROJECT']  # e.g. 'boilerplate'
    region_name = os.environ['AWS_REGION']  # e.g. 'us-west-2'
    environment = os.environ['ENVIRONMENT']  # e.g. 'staging'
    secret_full_name = f"{project}/{environment}/{secret_name}"
    endpoint_url = f"https://secretsmanager.{region_name}.amazonaws.com"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        endpoint_url=endpoint_url
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_full_name
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_full_name + " was not found")
        elif error.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", error)
        elif error.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", error)
        return None
    except NoCredentialsError as error:
        print("Unable to locate credentials, using defaults")
        return None
    else:
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response.get('SecretString')
        else:
            get_secret_value_response.get('SecretBinary')
            raise RuntimeError('Credentials should always be a string, not binary data.')

        return json.loads(secret)
