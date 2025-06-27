# **E-Commerce Microservices CI/CD Pipeline with Jenkins and AWS EKS**

This repository contains the source code for a microservices-based **E-commerce Application** built with 11 distinct microservices. The project is fully automated using **Jenkins** for Continuous Integration (CI) and Continuous Deployment (CD), and is deployed to **AWS EKS (Elastic Kubernetes Service)**. The entire pipeline is triggered automatically whenever code changes are pushed to the GitHub repository.

## **Project Overview**

In this project, we’re working on an e-commerce application with the following functionalities:

- **Email Service**: Sends notifications upon a successful purchase.
- **Cart Service**: Manages shopping cart functionality.
- **Shipping Service**: Handles shipping details and address management.
- **Frontend UI**: Displays all components in a user-friendly interface.
- **Payment Service**: Manages payment processing.

### **Key Features**
- **Microservices Architecture**: 11 individual microservices for various functionalities.
- **GitHub Integration**: Source code for each microservice is maintained in a dedicated branch.
- **Jenkins Multi-Branch Pipeline**: Automates build, test, and deployment for each microservice.
- **AWS EKS Deployment**: All microservices are deployed on AWS EKS.
- **Real-Time Automation**: Code pushes to GitHub automatically trigger the pipeline, ensuring real-time updates.

---

## **Project Setup**

### **1. Prerequisites**

Before you begin, make sure you have the following tools installed:

- **AWS CLI**: For interacting with AWS services.
- **kubectl**: Kubernetes command-line tool to interact with the EKS cluster.
- **eksctl**: A simple CLI tool to create and manage EKS clusters.
- **Jenkins**: For automating CI/CD processes.
- **Docker**: For building and pushing container images.

### **2. Setting Up the AWS Environment**

- **Create an AWS IAM User** with permissions for EKS (e.g., `AmazonEKSClusterPolicy`, `AmazonEC2FullAccess`).
- **Create an EKS Cluster** using the following command:
    ```bash
    eksctl create cluster --name=EKS-1 --region=ap-south-1 --zones=ap-south-1a,ap-south-1b --without-nodegroup
    ```
- **Set up IAM OIDC for EKS** to allow Kubernetes pods to assume IAM roles with minimal privilege access.

### **3. Jenkins Setup**

- Install **Java 17** and **Jenkins** on an EC2 instance. Follow the installation instructions for both:
    - Install Java 17:
      ```bash
      sudo apt install openjdk-17-jdk -y
      ```
    - Install Jenkins:
      ```bash
      wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
      sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
      sudo apt update
      sudo apt install jenkins -y
      ```
    - Access Jenkins via `http://<Public-IP>:8080`.
  
- **Install Docker** on the EC2 instance:
    ```bash
    sudo apt install docker.io -y
    ```
  
- **Install Jenkins Plugins** for Docker and Kubernetes integration:
    - Docker Plugin
    - Kubernetes CLI Plugin
  
- **Configure Jenkins** for GitHub, Docker, and Kubernetes.

---

## **CI/CD Pipeline**

### **1. Multi-Branch Pipeline**

We’ve created a Jenkins Multi-Branch Pipeline to automate the CI/CD pipeline for each microservice. Each microservice has its own branch with a **Jenkinsfile** containing the pipeline steps for building and deploying the respective service.

- **Pipeline Overview**:
    - **Build & Tag Docker Image**: Each microservice will have its own Docker image built and tagged.
    - **Push Docker Image**: Once the build is successful, the Docker image is pushed to **DockerHub**.
    - **Deploy to AWS EKS**: The Docker image is then deployed to the Kubernetes cluster on AWS EKS.

### **2. Triggering the Pipeline**

Whenever a push is made to any of the microservice branches on GitHub, the corresponding pipeline is automatically triggered through GitHub Webhooks and Jenkins Multi-Branch Pipeline functionality.

### **3. Kubernetes Deployment**

Once the Docker image is built and pushed, the deployment process is carried out using **Kubernetes YAML** files to deploy each microservice on AWS EKS. Jenkins interacts with the Kubernetes cluster using **KubeCredentials** and **kubectl** commands.

---

## **Deployment Workflow**

1. **Create a Namespace in Kubernetes**:
    ```bash
    kubectl create namespace webapps
    ```
2. **Create Kubernetes Service Account** and assign appropriate roles and permissions.
3. **Configure Kubernetes Deployment** for each microservice by creating corresponding Kubernetes YAML files.
4. **Deploy using Jenkins**:
    - The Jenkins pipeline will execute `kubectl apply` to deploy microservices on EKS.
    - Monitor the deployment using `kubectl get svc` to verify the services are up and running.

---

## **Environment Variables**

Ensure that the following environment variables are configured correctly:

- **AWS Access Keys**: For accessing AWS resources.
- **Kubernetes API Server URL**: For accessing EKS.
- **DockerHub Credentials**: For pushing Docker images.

---

## **Directory Structure**

├── cart-service/
│ ├── Dockerfile
│ ├── Jenkinsfile
│ └── ... (other service files)
├── email-service/
│ ├── Dockerfile
│ ├── Jenkinsfile
│ └── ... (other service files)
├── shipping-service/
│ ├── Dockerfile
│ ├── Jenkinsfile
│ └── ... (other service files)
├── frontend-ui/
│ ├── Dockerfile
│ ├── Jenkinsfile
│ └── ... (other service files)
└── infra-setup/
├── eks-cluster-setup.sh
├── cloudformation-template.yaml
└── main-branch/
├── deployment-service.yml
└── Jenkinsfile


### **Files Overview**:
- **Dockerfile**: Each microservice’s container configuration.
- **Jenkinsfile**: Defines CI/CD pipeline for the service.
- **deployment-service.yml**: Kubernetes deployment configuration for microservices.
- **infra-setup**: Infrastructure setup scripts (e.g., EKS cluster creation).

---

## **Accessing the Deployed Application**

Once the deployment is complete, you can retrieve the LoadBalancer URL by running:
kubectl get svc -n webapps
Use this URL to access your deployed application.

## **Cleaning Up Resources**
After testing, you can delete the Kubernetes cluster to free up resources:
eksctl delete cluster --name EKS-1 --region ap-south-1

Contributing
Feel free to fork this repository, create an issue, or submit a pull request with improvements or bug fixes!


