#configuration notes

## installation and configuration of a remote linux box (centos 6.x)
* https://sopel.chat/python3-centos7.html python3 sucks
* http://stackoverflow.com/questions/25010394/install-scipy-module-on-centos  scipy sucks
* 

## Docker configuration 
In the `docker/` subdirectory of this repo (as of dfd3e04d118) exists a dockerfile that specifies a python 3.5.x image that uses scipy and numpy (and other modules now required).  Scipy is particularly annoying; see above stack overflow link for why (you need LAPACK). 

On a machine with docker installed, where `$ROOT` is the base path of the repository:
```
cd $ROOT\docker
docker build -t gvoysey/thesis-code-python:v2 .  # or other distinct name
# wait for docker to finish up.
docker images 
#observe the _hash_ of the image; something like 0076f5ea.. or another sha
docker run -i -t <hash here> /bin/bash 
```

If on windows, Kitematic should now recognize that as a containerized thing that you can now configure PyCharm to use in its build settings. (see [this](https://blog.jetbrains.com/pycharm/2015/12/using-docker-in-pycharm/) link for how, but basically press `Alt+F7` and click buttons until it works.)