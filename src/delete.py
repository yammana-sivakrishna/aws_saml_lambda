# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import yaml

dynamodb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    # event is a parameter and a dictionary ex: {"id": 1, "Weather": "sunny"} 
    yaml_data = read_sam_template()
    tableName = taml_data["Resources"]["DynamoDBTable"]["Properties"]['TableName']
    # delete from WeatherData table based on key
    dynamodb_client.delete_item(TableName=tableName, Key=event)
    statusCode = 200
    statusMsg = 'Successfully deleted data!'

    return {
      'statusCode': statusCode,
      'body': statusMsg
    }

def read_sam_template(sam_template_fn = "template.yaml" ):
        """
        Utility Function to read the SAM template for the current project
        """
        with open(sam_template_fn, "r") as fp:
            template = fp.read().replace("!","")   # Ignoring intrinsic tags
            return yaml.safe_load(template)