# Прочти меня!

# for creating nginx image:
``` sh
docker build -f .\dockers\Dockerfile_nginx -t elvis_nginx_img .
```
# for create nginx container:
```sh 
docker run --name elvis_nginx -d -p 80:80 elvis_nginx_img
``` 

# for creating app image:
``` sh 
docker build -f .\dockers\Dockerfile_app -t elvis_app .
```
# for creating app container:
``` sh 
docker run --name elvis_app -d -p 5000:5000 elvis_app
```