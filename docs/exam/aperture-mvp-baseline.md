Hello!

Welcome to the technical portion of the interview process. We're excited to talk with you.

To help you prepare, this document outlines the baseline architecture for a fictional B2B SaaS product named "Aperture." The technical challenge during our interview will be to evolve this existing system. The goal is not to test your memory of these details, but to provide a common ground for a productive and collaborative architectural discussion. Please read through it beforehand so we can dive right into the fun part: problem-solving!

Aperture: The MVP Baseline

High-Level Context
Product: "Aperture" is a live B2B SaaS product that allows creative teams to upload photos and apply a single AI filter at a time.
Business Model: It currently serves about 1,000 active organizations on a single "starter" subscription plan. The system supports inviting multiple team members to an organization.
Scale & Growth: The platform is growing steadily at 20% month-over-month. We are noticing that a small number of "power user" organizations process thousands of photos, which is making their flat-rate plan unprofitable for us.

How it Works: The MVP Flow
The user experience is simple and fully synchronous.

A user uploads an image file. The platform currently has a known product limitation and only supports file uploads up to 4.5MB.
Our frontend application base64-encodes this file and sends it within a JSON payload to our REST API.
The backend processes the image by applying one filter. This entire operation is designed to complete in under 30 seconds.
The user's browser waits for the operation to finish and then receives a response containing the URL to the newly processed image.

Current Architecture & Tech Stack
The MVP was built for speed-to-market using a simple, synchronous, serverless design on AWS.

API: AWS API Gateway (HTTP API) forwards all incoming requests to a single Lambda function.
Compute: A single "Proxy" AWS Lambda written in Node.js with TypeScript handles all business logic, including authentication, metadata handling, and the image processing itself.
Storage:
Amazon S3 is used to store the original and processed image files.
Amazon DynamoDB is used for all metadata. All our logical entities are stored together in a single table to optimize access patterns.

Here is a diagram of the current architecture:


Logical Data Model
While all data resides in a single physical DynamoDB table, it is logically organized around the following entities:

User Entity:
userId
email
name
createdAt
Organization Entity:
organizationId
ownerId (maps to userId)
memberIds (List of user IDs)
plan (e.g., "starter")
Image Entity:
organizationId
imageId
status (e.g., "uploaded", "processed")
originalS3Key
processedS3Key
createdAt

What to Expect
This baseline is used for both pre-interview assessments and the live interview. During the assessment, you'll design solutions for specific scenarios. During the interview, we'll discuss your submission and may explore additional challenges.

During the interview, you will share your screen and use an AI tool of your choice as a brainstorming partner.

We look forward to collaborating with you!

