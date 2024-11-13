[![codecov](https://codecov.io/gh/digitalcorpora/digitalcorpora_app/branch/bottle-main/graph/badge.svg?token=E6GE1KIGAT)](https://app.codecov.io/gh/digitalcorpora/digitalcorpora_app/tree/bottle-main)

# digitalcorpora.org python app
This repo provides the custom-written Python code to for the https://DigitalCorpora.org/ website.

The website runs with WordPress. This repo runs in a sub-domain https://downloads.digitalcorproa.org/ provides the browsing functionality of the S3 bucket.  Our development website is https://dev.digitalcorpora.org/

The repo is designed to be check out as ~/downloads.digitalcorpora.org/ on a Dreamhost user account. It runs the python application in Bottle using the Dreamhost Passenger WSGI framework. The repo can also be checked out into other domain directories for development and testing. You can also modify the config file to browse other S3 buckets, should you wish to use this on another website.

# To setup
1. Copy in zappa_settings.json.  All defaults are here: https://github.com/zappa/Zappa/blob/master/example/zappa_settings.json
2. Update the file
3. Make sure that we have an app object from Flask() or bottle
4. Deploy and test.
5. Create a certificate for the subdomain *.domain.com at https://us-west-2.console.aws.amazon.com/acm/home?region=us-west-2#/certificates/request/public
6. Refresh the certificate list
7. Create the DNS entry for DNS certification. (only CNAME entry is needed, but a certificate may need to be issued for each region)
8. Create the domain


# aws deployment
- We used https://github.com/zappa/Zappa
- We stored the MySQL database credentials in the amazon Secrets Manager
- Lambda needs to be given access to the secrets manager and either all secrets or this specific secret. See:
  - https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html
  - https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_examples.html#auth-and-access_examples_read
  - https://docs.aws.amazon.com/secretsmanager/latest/userguide/troubleshoot_rotation.html

- We deployed to a URL:
- Need to move to a custom domain to get rid of the /production challen.

1 - Add the the layer named AWS Parameters and Secrets Lambda Extension. Specify verison 11.
2 - Click Configuration / Permission / Add Permissions
3 - Add permissions to an AWS service / Secrets Manager
4 - Add per

Try this:

1 - Go to the IAM Role Manager and find the role: https://us-east-1.console.aws.amazon.com/iam/home?region=us-west-2



Here is the policy:
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "SecretARN"
    }
  ]
}
```


# Other options
# - aws challice - completely different thing. new decorators

# Move to serverless:
https://www.serverless.com/blog/serverless-api-gateway-domain
https://www.serverless.com/examples/aws-python-flask-api
