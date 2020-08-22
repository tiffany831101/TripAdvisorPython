# TripAdvisor Web:
### Functionality 
* Search
![search](https://img.onl/sN77e)

* Restarant Info
![info](https://img.onl/WebhQ7)

* Register
![Register](https://img.onl/NCrPZL)

* Login
![Login](https://img.onl/s1eSpe)
![Forget Password](https://img.onl/hUrWhE)

* Following
![following](https://img.onl/nzihcs)
![followed](https://img.onl/oh8cE4)

* Restaurant Reservations
![reservation](https://img.onl/E3MCA)
![result](https://doc-00-08-docs.googleusercontent.com/docs/securesc/1qd851odt4r7pd2q31bv3l2gef4q4vlk/u878jtuppj2s8bnfqdfc3rr32fhcq0ar/1598062500000/12743253038928060072/02371497822323619930/1G4DQ_iHHpBFiaL2E9gd1E6ADppNJG_NO?authuser=1&nonce=n8qtgmhtp0pb8&user=02371497822323619930&hash=svbe8butjodm8qckvumipvqdufjog8nr)

* Comment
![comment](https://img.onl/bm3bMf)

* Member Home Pages
![home page](https://img.onl/E6NuSQ)



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