## Booth Registery

* to access server with the key:
```sh
ssh -i upgrade_sshkey.pem ec2-user@3.137.157.79
```

* running server can be view through tmux
```sh
tmux attach
```

* to inspect the docker contiainer:
```sh
docker exec -it upgradeboothregister /bin/sh
```
* to copy file out of container to ec2 instance
```sh
docker cp upgradeboothregister:/app/src/data.db ~/data.db
```

* to copy file out of ec2 instance to local machine
```sh
scp -i upgrade_sshkey.pem ec2-user@3.137.157.79:~/data.db ~/data.db 
```

these 2 can be achieved by navigating to scripts.and run:
```
./copyDataToLocal.sh
```