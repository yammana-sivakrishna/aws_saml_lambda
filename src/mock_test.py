# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from os import environ
import json
from datetime import datetime
from unittest import TestCase
from typing import Any, Dict
from uuid import uuid4
import yaml
import boto3
from boto3.dynamodb.conditions import Key
import moto


# Import the handler under test
from src import index

# Mock the DynamoDB Service during the test
@moto.mock_dynamodb

class TestSampleLambdaWithDynamoDB(TestCase):
    """
    Unit Test class for src/app.py
    """
    
    def setUp(self) -> None:
        """
        Test Set up:
           1. Create the lambda environment variale DYNAMODB_TABLE_NAME
           2. Build a DynamoDB Table according to the SAM template
           3. Create a random postfix for this test instance to prevent data collisions
           4. Populate DynamoDB Data into the Table for test
        """

        # Create a name for a test table, and set the environment
        self.test_ddb_table_name = self.read_sam_template()["Resources"]["DynamoDBTable"]["Properties"]['TableName']
        environ["DYNAMODB_TABLE_NAME"] = self.test_ddb_table_name 

        # Create a mock table using the definition from the SAM YAML template
        # This simple technique works if there are no intrinsics (like !If or !Ref) in the
        # resource properties for id, Weather
        sam_template_table_properties = self.read_sam_template()["Resources"]["DynamoDBTable"]["Properties"]
        self.mock_dynamodb = boto3.resource("dynamodb")
        self.mock_dynamodb_table = self.mock_dynamodb.create_table(
                TableName = self.test_ddb_table_name,
                id = sam_template_table_properties["id"],
                Weather = sam_template_table_properties["Weather"]
                )
   
        # Populate data for the tests
        self.mock_dynamodb_table.put_item(Item={"id": "10", 
                                                "Weather": "Rainy"})
        
    def tearDown(self) -> None:
        """
        For teardown, remove the mocked table & environment variable
        """
        self.mock_dynamodb_table.delete()
        del environ['DYNAMODB_TABLE_NAME']

    def read_sam_template(self, sam_template_fn : str = "template.yaml" ) -> dict:
        """
        Utility Function to read the SAM template for the current project
        """
        with open(sam_template_fn, "r") as fp:
            template = fp.read().replace("!","")   # Ignoring intrinsic tags
            return yaml.safe_load(template)

    def load_test_event(self, test_event_file_name: str) ->  Dict[str, Any]:
        """
        Load a sample event from a file
        Add the test isolation postfix to the path parameter {id}
        """
        with open(f"tests/events/{test_event_file_name}.json","r") as f:
            event = json.load(f)
            return event

    
    def test_lambda_handler_happy_path(self):
        """
        Happy path test where the id name record exists in the DynamoDB Table

        Since the environment variable DYNAMODB_TABLE_NAME is set 
        and DynamoDB is mocked for the entire class, this test will 
        implicitly use the mocked DynamoDB table we created in setUp.
        """

        test_event = self.load_test_event("sampleEvent_Found_TEST001")
        test_return = app.lambda_handler(event=test_event,context=None)
        self.assertEqual( test_return["statusCode"] , 200)
        self.assertEqual( test_return["body"] , "Successfully inserted data!") 

    def test_lambda_handler_notfound_path(self):
        """
        Unhappy path test where the id or Weather keys does not exist in the input JSON
        """

        test_event = self.load_test_event("sampleEvent_NotFound_TEST002")
        test_return = app.lambda_handler(event=test_event,context=None)
        self.assertEqual( test_return["statusCode"] , 404)
        self.assertEqual( test_return["body"] , "one of mandatory key missed.")

    def test_lambda_handler_morekeys_path(self):
        """
        Unhappy path test weather more keys exist in the input JSON
        """

        test_event = self.load_test_event("sampleEvent_NotFound_TEST003")
        test_return = app.lambda_handler(event=test_event,context=None)
        self.assertEqual( test_return["statusCode"] , 404)
        self.assertEqual( test_return["body"] , "JSON Contains more than required keys.")

        
        

    