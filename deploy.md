This is what I did to set up a deployment instance on AWS.
I think eventually the answer is to make a docker image.
Mostly following [this guide](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)


1. Set up an EC2 instance (t2.large with AWS linux running on it).
2. `sudo yum update -y`
3. `sudo yum install git -y`
4. `curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash`
5. `sudo yum install git-lfs`
4. `sudo yum groupinstall "Development Tools"`
4. `sudo yum install bzip2-devel readline-devel  ncurses-devel libffi-devel  openssl-devel`
4. `curl https://pyenv.run | bash`
5. Paste
    ```
    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    ```
6. re login
7. `pyenv install 3.9.16`
8. `pyenv global 3.9.16`
9. `git clone git@github.com:zhangir-azerbayev/mathlib-semantic-search.git`. If this doesn't work remember to use user-agent forwarding on ssh.
10. make an `.env` file and put values for
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - OPENAI_API_KEY
12. Splat this in `/etc/systemd/system/mathlib-search.service`
    ```ini
    [Unit]
    Description=Gunicorn instance of mathlib-semantic-search
    After=network.target

    [Service]
    User=ec2-user
    Group=ec2-user
    WorkingDirectory=/home/ec2-user/mathlib-semantic-search
    ExecStart=/home/ec2-user/.pyenv/shims/gunicorn --workers 1 --bind unix:mathlib-search.sock -m 007 src.web:app

    [Install]
    WantedBy=multi-user.target
    ```
12.  `sudo systemctl enable --now mathlib-search`
11. `sudo amazon-linux-extras enable nginx1`
12. `sudo yum -y install nginx`
13. `sudo systemctl enable --now nginx`
12. `mkdir /etc/nginx/sites-available`, `mkdir /etc/nginx/sites-enabled`
14. Put this in `/etc/nginx/sites-available/mathlib-search`
    ```
    server {
        listen 80;
        server_name mathlib-search.edayers.com;

        location / {
            proxy_pass http://unix:/home/ec2-user/mathlib-semantic-search/mathlib-search.sock;
        }
    }
    ```
12. `sudo ln -s /etc/nginx/sites-available/mathlib-search /etc/nginx/sites-enabled`

10. Make an elastic IP
11. Associate it to your EC2 instance.