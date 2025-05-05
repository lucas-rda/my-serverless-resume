# AWS Serverless Resume Website

![Project Architecture](./architecture.jpg)

## Project Overview
A cloud-based resume website with a visitor counter and location tracking, built using AWS serverless technologies. This project demonstrates practical experience with AWS services, API development, and full-stack implementation.

## Live Demo
🔗 [View my resume](https://lucas-albuquerque.com)

## Features
- Static website hosted on S3 and distributed via CloudFront
- Serverless API with AWS API Gateway and Lambda
- Visitor counter with geolocation tracking
- Display of recent visitors with country flags
- Multi-language support (English/Portuguese)
- Mobile-responsive design with dark mode

## Architecture
This project utilizes the following AWS services:
- **Amazon S3** - Static website hosting
- **Amazon CloudFront** - Content delivery network
- **AWS Lambda** - Serverless backend functions
- **Amazon DynamoDB** - NoSQL database for visitor data
- **Amazon API Gateway** - RESTful API endpoints
- **IAM** - Security and permissions

## Technical Implementation
### Frontend
The frontend is a static HTML/CSS/JavaScript website that:
- Displays professional information in a responsive layout
- Communicates with the backend API to fetch and display visitor data
- Supports toggling between dark/light mode and multiple languages

### Backend
The backend consists of two Lambda functions:
1. **visitor-logger** - Captures visitor IP, determines geographic location, and increments the counter
2. **get-visits** - Retrieves overall count and recent visitor information

### Database
DynamoDB stores:
- A total visitor count
- Individual visitor records with IP, timestamp, country, city, and flag emoji
- A GSI for IP-based deduplication

## Challenges Overcome
- Implemented IP tracking with 24-hour deduplication
- Set up proper CORS configuration between S3 and API Gateway
- Created an efficient DynamoDB schema for visitor tracking

## Learning Outcomes
This project enhanced my skills in:
- Serverless architecture design
- AWS service configuration and integration
- API development and security
- NoSQL database design
- JavaScript interaction with backend services

## Repository Structure
- `/frontend` - Website HTML, CSS, and JavaScript files
- `/backend` - Python Lambda function codes


## Future Enhancements
- Add CI/CD pipeline with GitHub Actions
- Implement visitor analytics dashboard
- Add multi-region deployment for improved resilience

## Contact
Feel free to reach out if you have any questions about this project!
