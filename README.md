# SneakerDealer 👟

Welcome to the SneakerDealer project, a cutting-edge platform designed for the vibrant community of sneaker enthusiasts and collectors and allows users to share, buy, sell or trade sneakers.

At its core, SneakerDealer leverages a microservices architecture to ensure scalability, flexibility, and efficient performance. With separate services for user management and product listings, the application is structured to handle complex workflows and high traffic volumes seamlessly. 

The project employs robust databases to manage and store data securely, ensuring fast and reliable access to information. This architectural choice not only enhances the application's performance but also facilitates easier maintenance and scalability.

## Quick Start 🏁

### Prerequisites 📋

- Docker
- Docker Compose
- python3
- pytest

To get started, ensure you have Docker and Docker Compose installed on your system. Installation instructions can be found in the [official Docker documentation](https://docs.docker.com/get-docker/).

### Installation 🛠️

1. Begin by cloning the repository to your local machine:
    ```
    git clone https://github.com/Matanzor/SneakerDealer.git
    ```
2. Navigate into the project directory:
    ```
    cd SneakerDealer
    ```

### Accessing the Application

1. Use Docker Compose to start the application:
    ```
    docker-compose up --build
    ```
2. Once the containers are operational, the application's front-end can be accessed at `http://localhost:8501`.

### Testing ✔️

To execute tests, do the following:
1. Comment lines 7, 8 in backend/users_service/main.py & uncommment lines 9, 10 in the same file.
2. Comment lines 8, 9 in backend/posts_service/main.py & uncommment lines 10, 11 in the same file.
3. run 'pytest <path_to_testfile>'


### Features

- **Microservices Architecture**: Modular design allowing for independent development, deployment, and scaling of services.
- **User Authentication**: Secure system for user registration and login, protecting user data and access.
- **Marketplace Functionality**: Platform for users to list their sneakers for sale and explore offerings from others.
- **Responsive UI**: Engaging and intuitive user interface crafted with Streamlit, ensuring a smooth user experience.


### Project's Diagram 📈

![alt text](https://github.com/Matanzor/SneakerDealer/blob/master/Sneakers_project_draw.PNG)

### View Demo 📽️

Link to YouTube video: https://www.youtube.com/watch?v=fPa3e4NP1RA

Enjoy our Sneakers community! 😋

