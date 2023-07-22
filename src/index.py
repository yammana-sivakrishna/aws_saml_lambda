# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import yaml

dynamodb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
  # event is a parameter and a dictionary ex: {"id": 1, "Weather": "sunny"} 
  # Default values for status and message parameters
  statusCode = 404
  statusMsg = None

  # id or Weaher keys checking weather both keys present or not
  if "id" not in event or "Weather" not in event:
    statusMsg = "one of mandatory key missed."
  # Extra keys checking
  if "id" in event and "Weather" in event and len(event) == 2:
    yaml_data = read_sam_template()
    tableName = taml_data["Resources"]["DynamoDBTable"]["Properties"]['TableName']
    # Updating id and Weather in WeatherData table
    dynamodb_client.put_item(TableName=tableName, Item={'id': {'S': event['id']}, 'Weather': {'S': event['Weather']}})
    statusCode = 200
    statusMsg = 'Successfully inserted data!'
  else:
    statusMsg = "JSON Contains more than required keys."

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
