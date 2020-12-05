# TripAdvisor Web:

### Web Interface 
#### Home
![home](https://img.onl/X8pUFn)

#### Restarant Info
![info](https://img.onl/LFsExi)

#### Restaurant Reservations
![reservation](https://img.onl/XJny0R)
![result](https://img.onl/1g0Q2d)

#### Member Home
![home page](https://img.onl/G4y7WC)

#### Following
![following](https://img.onl/nzihcs)
![followed](https://img.onl/oh8cE4)


#### Comment
![comment](https://img.onl/nqO1I)



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


#### Install Docker
```
$ sudo apt-get update

$ sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common

$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

$ sudo apt-key fingerprint 0EBFCD88

$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu
$(lsb_release -cs)
stable"

$ sudo apt-get update

$ sudo apt-get install docker-ce docker-ce-cli containerd.io
```

#### Install Docker Compose
```
$ sudo apt install docker-compose
```

#### Deploy TripAdvisor Project
```
$ cd docker_stg
$ sudo docker-compose up --build -d
```
* It wills automatically create tables in MySQL and build website.

#### Monitor Website
* http://localhost:3000/

![monitor](https://img.onl/Nwbz4c)
