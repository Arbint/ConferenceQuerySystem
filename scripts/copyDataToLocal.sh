#!/bin/bash
ssh -i ../upgrade_sshkey.pem ec2-user@3.137.157.79 'docker cp upgradeboothregister:/app/data/data.db ~/data.db'
scp -i ../upgrade_sshkey.pem ec2-user@3.137.157.79:~/data/data.db ../data.db 