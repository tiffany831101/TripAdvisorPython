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
* Monitoring : Supervisor, flask-exporter, mysql-exporter
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


#### MySQL Configuration
```
$ vim /etc/mysql/mysql.cnf
```

```
[mysqld]
bind-address = *

expire_logs_days = 10

connect_timeout = 120
net_read_timeout = 7200

max_connections = 3000
max_allowed_packet = 128M
group_concat_max_len = 102400

slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 2
```

#### Monitor Website
* http://localhost:3000/

![monitor](https://img.onl/Nwbz4c)



#### Monitor MySQL
* http://localhost:3000/
![monitor](https://img.onl/ALxPqy)
