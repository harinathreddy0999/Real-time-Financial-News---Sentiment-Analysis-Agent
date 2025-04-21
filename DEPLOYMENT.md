# Deployment Strategy for Financial News Agent

This document outlines the steps to build and deploy the containerized Financial News & Sentiment Analysis Agent.

## Prerequisites

*   Docker installed and running.
*   Access to a command line/terminal.
*   (Optional) Access to a container registry (Docker Hub, AWS ECR, Google GCR, etc.) if deploying remotely.
*   A configured `config/.env` file containing the necessary API keys **(DO NOT commit this file to Git)**.

## 1. Building the Docker Image

Navigate to the project's root directory (where the `Dockerfile` is located) in your terminal and run:

```bash
docker build -t financial-agent:latest .
```

*   `-t financial-agent:latest`: Tags the built image with the name `financial-agent` and the tag `latest`.
*   `.`: Specifies the current directory as the build context.

## 2. Pushing to a Container Registry (Optional)

If deploying to a cloud environment or Kubernetes, you'll likely need to push the image to a registry.

1.  **Tag the image for your registry:**
    ```bash
    # Example for Docker Hub
    docker tag financial-agent:latest your-dockerhub-username/financial-agent:latest
    
    # Example for AWS ECR (replace placeholders)
    # aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-aws-account-id.dkr.ecr.your-region.amazonaws.com
    # docker tag financial-agent:latest your-aws-account-id.dkr.ecr.your-region.amazonaws.com/financial-agent:latest
    ```

2.  **Push the image:**
    ```bash
    # Example for Docker Hub
    docker push your-dockerhub-username/financial-agent:latest
    
    # Example for AWS ECR
    # docker push your-aws-account-id.dkr.ecr.your-region.amazonaws.com/financial-agent:latest
    ```

## 3. Running the Container

How you run the container depends on your target environment.

**A) Running Locally (for testing/development):**

```bash
docker run --rm -it \
    --env-file config/.env \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/logs:/app/logs \
    financial-agent:latest 
```

*   `--rm`: Automatically remove the container when it exits.
*   `-it`: Run in interactive mode with a pseudo-TTY (useful for seeing logs directly).
*   `--env-file config/.env`: Loads environment variables (including secrets) from your local `.env` file.
*   `-v $(pwd)/data:/app/data`: Mounts the local `data` directory into the container at `/app/data` for persistent data storage.
*   `-v $(pwd)/logs:/app/logs`: Mounts the local `logs` directory into the container at `/app/logs` for persistent log storage.

**B) Running on a Cloud Service (Conceptual Steps):**

*   **Choose a Service:** AWS ECS, Google Cloud Run, Azure Container Instances, etc.
*   **Define Task/Service:** Configure the service to use your container image (e.g., `your-registry/financial-agent:latest`).
*   **Inject Secrets:** Use the cloud provider's recommended method for handling secrets. **Do not** hardcode keys in the container definition. Options include:
    *   Injecting environment variables securely (e.g., from AWS Secrets Manager, Google Secret Manager, Azure Key Vault).
    *   Mounting secret volumes.
*   **Configure Volumes (Optional):** If you need data/logs to persist beyond the container instance lifecycle on the cloud platform, configure persistent volume mounts (e.g., using EFS on AWS, Filestore on GCP, Azure Files).
*   **Set Resources:** Allocate appropriate CPU and memory.
*   **Deploy & Monitor:** Deploy the service and set up logging/monitoring integrations.

**C) Running on a Server/VM:**

1.  Ensure Docker is installed on the server.
2.  Pull the image from the registry (if applicable): `docker pull your-registry/financial-agent:latest`.
3.  Create necessary directories on the host (e.g., `/opt/financial-agent/data`, `/opt/financial-agent/logs`).
4.  Create a `.env` file on the host (e.g., `/opt/financial-agent/config/.env`) with the required API keys.
5.  Run the container (potentially detached using `-d`):
    ```bash
    docker run -d --name financial-agent --restart always \
        --env-file /opt/financial-agent/config/.env \
        -v /opt/financial-agent/data:/app/data \
        -v /opt/financial-agent/logs:/app/logs \
        your-registry/financial-agent:latest
    ```
    *   `-d`: Run in detached mode (background).
    *   `--name financial-agent`: Assign a name to the container.
    *   `--restart always`: Automatically restart the container if it stops.
6.  **Manage with Systemd (Recommended):** Create a systemd service file to manage the Docker container lifecycle (start, stop, restart, view logs via `journalctl`).

## 4. Monitoring

Regardless of the deployment method, monitor the agent:

*   **Container Metrics:** Track CPU and memory usage.
*   **Logs:** Regularly check the container logs (via `docker logs`, cloud provider logging, or the mounted log file) for errors or warnings.
*   **Application Alerts:** Monitor the configured Slack channel (or other alert channels) for notifications generated by the agent.
*   **External Service Status:** Be aware of the status and rate limits of the APIs being used (News API, LLM API). 