# Example Serverless Web app

This is a very simple serverless python application. 

It features basic authentication and a webpage using git and Amplify, while keeping track of logged in users on DynamoDB using a python based AWS Lambda function.


## Cloud infrastructure

The app requires:

- Amplify to manage the webapp
- Github or CodeCommit to maintain the frontend code
- Cognito to provide basic authentication
- Lambda and API gateway to keep track of users logins
- DynamoDB as log backend


## Git

We are going to maintain the webapp on AWS CodeCommit. This is allowing us to later integrate it into a CI/CD pipeline, if we want to.

Create a new repository on CodeCommit, let's call it "TestApp", and get a new SSH key for codecommit on the user's AWS account.


## Webapp deployment: AWS Amplify

The application is deployed using AWS Aplify. From the AWS console, open the Amplify service webpage and select "All apps", then "Host your app".

The wizard allows to select from different git services, we are going to select the codecommit's repo we've defined above.

Clone the git repo locally, and add a single `index.html` page and push back upstream.


## User management option: AWS cognito

Cognito can help us to manage the webapp users. In order to use it anyway, we need to integrate it into the webapp, on codecommit.

This can be done easily with some `javascript` code, see https://github.com/aws-amplify/amplify-js/tree/master/packages/amazon-cognito-identity-js

You can make use of App clients on Cognito to enable authentication on the webapp.


## Lambda function

On AWS, search for the Lambda service, set "TestApp" as Function name and select Python 3.9 as Runtime.

By default, the Lambda function provides minimal access to AWS (basically only logging).

To read and write from DynamoDB, we need to add some more permissions to the function. We can achieve this either by creating a new role and assign it to the Lambda function by clicking `Change default execution role` on the function's creation page and select "Use an existing role" or let the wizard create the role for you, and add more permissions later.

To enable the function to use DynamoDB, go on the IAM service webpage, click on Roles, search for the role name created for the function (manually or by the wizard) and modify it to allow `dynamodb`

```
"logs:CreateLogStream",
"logs:PutLogEvents",
"dynamodb:*"
```

Once the function is ready, you can chose a trigger for it, such as AWS API Gateway.


### Info about the Lambda function

The python code is checking if the event's body has a `username` or a `last` key in it.

If `username` is proviced, then the code will fetch some data, such as IP and agent, and it will store that into DynamoDB.

If `last` is found as key, then the function will return all the login date/time related the user by querying DynamoDB.

If the data sent is valid, then the return code will be `200` and, in a cloud deployment, it would make the source aware that the API call worked.

The returned data can be then elaborated by a client application to show the last logins on a webpage.


## API gateway

On the function's web page, click on "Triggers" and select "API Gateway".

Select `HTTP API` as "API type", select "Open" as security and clock on "Add".

If everything is working correctly, the Lambda function will return a default message to any call on port 443, ie:

```
curl https://<API_GATEWAY_ENDPOINT>
"Hello from Lambda!"
```


## DynamoDB

Deploy a new table on DynamoDB (let's call it `testapp`), and 2 indexes: one for the `timestamp` and another for `username`.


## Deploy the code

Select the "Code" tab on the lambda function, and paste the code from this repo, `lambda_function.py` into the Code editor.


## Option: Alerting via SNS

SNS can be optionally set as destination to the lambda function to get alerts from any login, for example by email


## Quick test

The lambda function and its API gateway are up and running:

```
# This will add a new entry to DynamoDB related the "matt" user

curl -X POST https://cv5dhgi71i.execute-api.eu-west-2.amazonaws.com/default/cloudbot -H 'Content-Type: application/json' -d '{"username":"matt"}' | jq
{
  "timestamp": 1639010147970,
  "username": "matt",
  "datetime": "01/Dec/2020:01:02:03 +0000",
  "accountId": "123456789123",
  "sourceIp": "1.2.3.4",
  "userAgent": "curl/7.29.0"
}

# This will list all logins related the user "matt" set as value

curl -X POST https://cv5dhgi71i.execute-api.eu-west-2.amazonaws.com/default/cloudbot -H 'Content-Type: application/json' -d '{"last":"matt"}' | jq
[
  "matt: 01/Dec/2020:00:13:28 +0000",
  "matt: 01/Dec/2020:00:13:45 +0000",
  "matt: 01/Dec/2020:00:19:48 +0000",
  "matt: 01/Dec/2020:00:04:43 +0000"
  ]
  
# Any other value will return an error

curl -X POST https://cv5dhgi71i.execute-api.eu-west-2.amazonaws.com/default/cloudbot -H 'Content-Type: application/json' -d '{"lasr":"matt"}' | jq
ERROR: No username or last sent as key
```
