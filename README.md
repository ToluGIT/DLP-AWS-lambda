# DLP-AWS-lambda

In this Project, we will be using AWS Macie to scan S3 for PII with post-action via EventBridge, Lambda and SNS to automate responses by moving identified PII files to an S3 bucket (with an additional layer of encryption)  and sending notifications to alert stakeholders about sensitive data activity.

It will be deployed in the us-east-1 region, make sure you change the region if you're deploying in another region.

Also, Macie is free for 30 days, so you won't need to pay for anything as long as it's disabled and not in use within the time frame.

For this project, we will be using the following data for PII detection

************************Credit card details - tester.txt************************

```python
American Express
5157528008183443 09/28
CVE: 567

Mastercard
5205105175105100
Exp: 01/27
Security code: 07/26


American Express
657965527580785 01/29
CCV: 9723

```
Other sample data can be used depending on the use case such as Employee information, License plates, and credential keys (AWS, Github and so on)

# Steps to follow 

## Step 1 - Add the example data to S3

Save each of the example data files as individual text files on your computer, Open the S3 console by visiting: https://s3.console.aws.amazon.com/s3/buckets

Create a new bucket:

 * Click on <kbd>Create bucket</kbd>
 * Enter a name of your choice and select the desired region (ensure it matches the region where you have set up Macie), Leave all other options as default and <kbd>Create bucket</kbd>.

**********Note:********** Ensure the bucket region is the same as the Macie region.

Upload the saved files to the new S3 bucket:

 * You can upload them directly to the root directory of the bucket or organize them into a subdirectory if you prefer.

An additional bucket is created to store the PII object upon detection by Macie, and an extra layer of encryption can be added such as:

 * Server-side encryption with Amazon S3 managed keys (SSE-S3) - The default encryption uses AES-256 encryption
 * Server-side encryption with AWS Key Management Service keys (SSE-KMS) - AWS KMS-managed keys
 * Dual-layer server-side encryption with AWS Key Management Service keys (DSSE-KMS) - Dual Layer KMS keys

**********Note:********** Take note of both buckets names.

## Step 2 - Enable Amazon Macie

Go to the Macie console by visiting this link: [https://us-east-1.console.aws.amazon.com/macie/home?region=us-east-1#getStartedQuick](https://us-east-1.console.aws.amazon.com/macie/home?region=us-east-1#getStartedQuick)

After clicking <kbd>Getting started</kbd>, you'll see an introduction to Amazon Macie, detailing the service-linked role that AWS creates to enable Macie to scan S3 buckets.

To continue, <kbd>Enable Macie</kbd>.

Once enabled, you may need to wait a few minutes and refresh the page occasionally until Macie is fully ready to display the main dashboard screen.

it should look similar to this

![image](https://github.com/user-attachments/assets/f885849c-b96b-4940-969b-d1947468dbc0)

Navigate to the S3 Buckets section, select the checkbox next to the bucket you created and uploaded the example data to, and then  <kbd>Create job</kbd>.

![2 2](https://github.com/user-attachments/assets/d104f4b7-7e27-46b5-9f93-9717b1c6aa93)

Click <kbd>Next</kbd> on the Review S3 buckets page.

Under Refine the scope, choose One-time job and proceed by clicking <kbd>Next</kbd>. 

**Note:** You also have the option to set it as a scheduled job run daily, weekly or monthly  with an option to include/exclude existing objects and in the additional sittings - the option to set criteria that determine which objects to include or exclude from the job’s analysis. If you don’t enter any criteria, the job analyzes all objects in the buckets.

Ensure Managed data identifier options remain recommended and continue with <kbd>Next</kbd>.

With no Custom data identifiers available, simply click <kbd>Next</kbd>.

Advance past the “Select allow lists” page by selecting <kbd>Next</kbd>.

Name the “Job” with any preferred name and hit <kbd>Next</kbd>.

Double-check the configuration, and if everything appears correct, click <kbd>Confirm</kbd>.

**Note:** In cases whereby the objects are encrypted with customer-managed AWS KMS keys, ensure that Macie is allowed to use the key for more information visit this [link](https://docs.aws.amazon.com/macie/latest/user/discovery-supported-encryption-types.html)

it takes a couple of minutes to complete the analysis, once done you can click on <kbd>show results</kbd> then <kbd>show findings</kbd> to see the identified PII data detected


![10](https://github.com/user-attachments/assets/008e7906-516e-437c-a463-f060eaeeaad8)


![11](https://github.com/user-attachments/assets/5f740d49-939d-43a5-b6fe-243e44ce44f1)


Now that we have been able to identify the PII from the object files, we can proceed to automate post-action after detection.

Before doing this, we need to set, EventBridge and Lambda

## Step 3 - Configure SNS

Go to the SNS console by visiting this link: [https://us-east-1.console.aws.amazon.com/sns/v3/home?region=us-east-1#/topics](https://us-east-1.console.aws.amazon.com/sns/v3/home?region=us-east-1#/topics)


Select <kbd>Create topic</kbd>.

Choose <kbd>Standard</kbd> as the <kbd>Type</kbd>.

Enter “your preferred topic name” for the Name.

In the Access Policy section, keep the Method set to “Basic”.

Adjust “Specify who can publish messages to the topic” to “Only the specified AWS accounts” and input your account ID.

Adjust "Specify who can subscribe to this topic." to “Only the specified AWS accounts” and input your account ID again

Keep all other options at their default settings.

Select <kbd>Create topic</kbd>.

On the following page, choose <kbd>Create subscription</kbd>.

Set the Protocol to “Email”.

Enter your personal email in the Endpoint field.

Click <kbd>Create subscription</kbd>.

A confirmation email will be sent to you shortly with a link to confirm your subscription. Clicking the link indicates your consent to receive emails from the topic and helps prevent spam from being sent via SNS.

![3](https://github.com/user-attachments/assets/2087bd1b-e576-446a-a370-2758240ffeec)

Your subscription should now be in the Confirmed state:

![4](https://github.com/user-attachments/assets/f3ac3b16-56bb-431a-a82b-edd11d0d827e)

Take note of the ARN for the SNS subscription, we will make reference to it later on.

## Step 5 - Configure Lambda

Go to the Lambda console by visiting this link: [https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/discover](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/discover)

Select <kbd>Create function</kbd>.

On the following page, choose <kbd>Author from scratch</kbd>.

Set the “Function name” to your preferred name 

Set the “Runtime” to <kbd>Python 3.12</kbd>. 

***********I used the Python runtime here. If another runtime is preferred, the code must be adjusted to meet the runtime's requirements.***********
***********Leave the remaining default settings, if an existing execution role is created, this can be used, or a new role with basic Lambda permissions is created by default***********

Once created modify the <kbd>code source</kbd>.

Click on "Code"

A code sample exists, modify it with the content as seen in the lambda_function.py file in the Github repo

The following values will need to be changed depending on your current setup

**SOURCE_BUCKET_NAME** - The S3 bucket to be monitored for PII
**DESTINATION_BUCKET_NAME** - The S3 bucket where the PII object will be moved 

Once it's modified then save.

**********Note:********** We will come back to setup the Trigger and Destination later. For now, take note of the Lambda name.

## Step 5 - Configure EventBridge

Go to the EventBridge console by visiting this link: [https://us-east-1.console.aws.amazon.com/events/home?region=us-east-1#/](https://us-east-1.console.aws.amazon.com/events/home?region=us-east-1#/)

Ensure “EventBridge Rule” is selected, then click <kbd>Create rule</kbd>.

![5](https://github.com/user-attachments/assets/8cb84feb-6ad8-430e-b939-bd88224030dc)

Set the “Name” to your preferred name on the next page, keep all other settings as default, with the Rule type set to "Rule with an event pattern" and click <kbd>Next</kbd>.

On the next page scroll down to "Creation method" and select "Use Pattern form".

Scroll further down to "Event Pattern" then Change “AWS Service” to “Macie”, and “Event Type” to “Macie Finding”

it should look similar to this

![image](https://github.com/user-attachments/assets/721c0fc9-4450-4001-a1bd-9a3400a11849)

Afterwards, Click <kbd>Next</kbd>.

Select Target Type as “AWS service” on the next page, then choose “Lambda” and select the Lambda function created earlier.

![7](https://github.com/user-attachments/assets/3ee016db-2d16-4160-b93a-1279706eb475)

If tags are not reviewed, Click <kbd>Skip to review and create</kbd>.

Once created, go back to the previously created Lambda function; here we notice the EventBridge created has been added as a trigger.

Proceed to add the destination of the lambda function by clicking on <kbd>+ Add destination</kbd>.

On the following page 

Select <kbd>Asynchronous invocation</kbd> for the Source.

Select <kbd>On success</kbd> for the Condition.

Select <kbd>SNS Topic</kbd> for the Destination type.

Choose the ARN of the <kbd>destination</kbd> (the SNS topic created earlier) for the Destination

Click <kbd>Save</kbd>.

![8](https://github.com/user-attachments/assets/02cfa5c7-dcef-4343-bdaa-8ddbd46c8ca8)

The Lambda Function Overview should look similar to this

![9](https://github.com/user-attachments/assets/98d32e97-29c3-4700-a575-617594cb94d8)

## Step 6 - Creating a new job

Go back to the Macie Console once more by visiting this link: [https://us-east-1.console.aws.amazon.com/macie/home?region=us-east-1#summary](https://us-east-1.console.aws.amazon.com/macie/home?region=us-east-1#summary)

Head over to the “S3 Buckets” section, select the checkbox next to the bucket you created and added the file to, then click <kbd>Create job</kbd>.


![2 2](https://github.com/user-attachments/assets/8aa4e6d3-f81e-42e1-ac69-6e82128a8403)

Click <kbd>Next</kbd> on the Review S3 buckets page.

Under Refine the scope, choose One-time job and proceed by clicking <kbd>Next</kbd>. 


Ensure Managed data identifier options remain recommended and continue with <kbd>Next</kbd>.

With no Custom data identifiers available,  click <kbd>Next</kbd>.

Advance past the “Select allow lists” page by selecting <kbd>Next</kbd>.

Name the “Job” with any preferred name and hit <kbd>Next</kbd>.

Double-check the configuration, and if everything appears correct, click <kbd>Confirm</kbd>.

Within a few minutes, you should receive an email notification containing JSON outputs of the Macie findings similar to this.

![13](https://github.com/user-attachments/assets/df37edf6-f8b9-494f-8914-29cb09e8a7cf)

Let's confirm, Lambda action also moved the sensitive data to the encrypted s3 bucket as expected.

This is the source bucket with the sensitive data (before running Macie)

![12](https://github.com/user-attachments/assets/5642629e-3275-4d00-a677-270e4eebe3f2)


This is the destination bucket with the moved sensitive data (after running Macie)

![14](https://github.com/user-attachments/assets/511cf1ed-ddfc-4928-8189-2904f1b8fb7e)

## Step 7 - The Clean up

Head to the SNS console: [https://us-east-1.console.aws.amazon.com/sns/v3/home?region=us-east-1#/topics](https://us-east-1.console.aws.amazon.com/sns/v3/home?region=us-east-1#/topics)

Select the created Topic and click <kbd>Delete</kbd>

Type “delete me” into the confirmation field, and click <kbd>Delete</kbd>

Now go to the Subscriptions page, select your subscription, click <kbd>Delete</kbd>, and then <kbd>Delete</kbd>

Head to the Macie Console: [https://us-east-1.console.aws.amazon.com/macie/home?region=us-east-1#summary](https://us-east-1.console.aws.amazon.com/macie/home?region=us-east-1#summary)
.
Go to Settings, and scroll to the end of the page, where there will be a <kbd>Disable Macie</kbd> button. Click on that, type “Disable” in the confirmation box, and click <kbd>Disable Macie</kbd>.

Head to the EventBridge console: [https://us-east-1.console.aws.amazon.com/events/home?region=us-east-1#/dashboard](https://us-east-1.console.aws.amazon.com/events/home?region=us-east-1#/dashboard)

Go to the Rules page, select the rule we created earlier, and click <kbd>Delete</kbd>

Type the name of the rule in the confirmation box, and click <kbd>Delete</kbd>

Head to the S3 console: [https://us-east-1.console.aws.amazon.com/s3/buckets?region=us-east-1](https://us-east-1.console.aws.amazon.com/s3/buckets?region=us-east-1)

Select your source bucket, and click <kbd>Empty</kbd>

Enter “*permanently delete”* in the confirmation window, and click <kbd>Empty</kbd>

Select your Destination bucket, and click <kbd>Empty</kbd>

Enter “*permanently delete”* in the confirmation window, and click <kbd>Empty</kbd>


## Conclusion

With this project, we've successfully implemented an end-to-end data loss prevention solution using AWS services to detect and handle sensitive PII data within S3. Amazon Macie enabled the identification of PII within specified S3 buckets, and using EventBridge, Lambda, and SNS, we automated responses to detected findings by moving the identified PII files to a more secure bucket with an additional layer of encryption and notifying relevant stakeholders through SNS alerts.


Feel free to further enhance this solution by adding custom data identifiers, fine-tuning EventBridge rules, or expanding Lambda's functionality to cover additional use cases.
