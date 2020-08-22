# TripAdvisor Web:
### Functionality 
* Search

* Register

* Login

* Following

* Restaurant Reservations

* Comment

* Member Home Pages

* Track User Behavior

# How to deploy TripAdvisor project ? 
### Enviroment:
* Ubuntu: 16.04 
* Python: 3.5.2
* Backend: Flask Framework
* Asynchronous: Celery
* Monitoring : Supervisor
* Frontend: Javascript (JQuery)
* Deploy: Docker, Docker Compose
* Reverse proxy: Nginx
* Database: Redis, MySQL


### Install Docker
* sudo apt-get update

* sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common

* curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

* sudo apt-key fingerprint 0EBFCD88

* sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu
$(lsb_release -cs)
stable"

* sudo apt-get update

* sudo apt-get install docker-ce docker-ce-cli containerd.io


### Install Docker Compose
* sudo apt install docker-compose


### Deploy 
* cd docker_stg
* sudo docker-compose up --build -d


### Migrate MySQL
* source env/bin/activate
* python3 manage.py db init
* python3 manage.py db migrate