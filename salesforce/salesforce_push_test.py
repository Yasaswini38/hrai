from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os

load_dotenv()

sf = Salesforce(
    username=os.getenv("SF_USERNAME"),
    password=os.getenv("SF_PASSWORD"),
    security_token=os.getenv("SF_TOKEN")
)

# Test by creating dummy record
result = sf.Candidate__c.create({
    "Name": "Integration Test Candidate",
    "Full_Resume_Text__c": "Python, Data Science, Machine Learning",
    "Predicted_Status__c": "Hire",
    "Hire_Probability__c": 0.92
})

print("Record created successfully:", result)
