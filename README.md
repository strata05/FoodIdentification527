# Food Identification Project

A full-stack web application for food image upload, storage, and analysis.  
Backend: FastAPI + DynamoDB + S3 (AWS)  
Frontend: React + TailwindCSS

## Features

- Server-side API with FastAPI  
- Secure user authentication and registration  
- Image upload and storage in AWS S3  
- Metadata management with AWS DynamoDB  
- Image analysis functionality (model integration)  
- Frontend built with React, TypeScript, and TailwindCSS

## Getting Started

### Installation

Clone the repository and install dependencies:

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

### Backend

Navigate to the `python/` folder, create a Python virtual environment, and install dependencies:

```bash
cd python
conda activate myenv
pip install -r requirements.txt
```

Run the backend service:

```bash
python -m uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

---

## AWS Configuration

This project uses **Amazon DynamoDB** and **Amazon S3**.  
To run the application successfully, each developer must configure AWS credentials locally.

1. **Create an IAM User** (with DynamoDB and S3 access):
   - Log in to AWS Management Console  
   - Go to **IAM → Users → Add users**  
   - Select **Programmatic access**  
   - Attach policies:  
     - `AmazonDynamoDBFullAccess`  
     - `AmazonS3FullAccess` (or a more restrictive custom policy)

2. **Configure AWS CLI** (one-time setup):
   ```bash
   aws configure
   ```
   Enter your credentials when prompted:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Default output format (e.g., `json`)

   Credentials will be saved to:
   - `~/.aws/credentials`
   - `~/.aws/config`

3. **Environment Variables (Optional)**  
   Alternatively, set credentials via environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

Once configured, boto3 (Python AWS SDK) will automatically detect your credentials. No secrets should be hardcoded into the project source code.

---

## Building for Production

To build the frontend for production:

```bash
npm run build
```

The output will be in the `build/` directory.

---

## Deployment

### Docker Deployment

Build and run with Docker:

```bash
docker build -t food-identification .
docker run -p 3000:3000 food-identification
```

You can deploy the container to any cloud platform supporting Docker, including AWS ECS, Google Cloud Run, or Azure Container Apps.

### Manual Deployment

If deploying manually, ensure:
- Frontend build artifacts are served
- Backend is running with proper AWS access
- Environment is correctly configured with AWS credentials

---

## Styling

This project uses [Tailwind CSS](https://tailwindcss.com/) for UI styling.
