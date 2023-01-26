This is what I did to set up a deployment instance on AWS.
I think eventually the answer is to make a docker image.
Mostly following [this guide](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04).

1. Set up an EC2 instance (t2.large with Ubuntu running on it).

    ```sh
    # install stuff
    sudo apt update
    sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
    sudo apt-get install git-lfs

    # nginx
    sudo apt install nginx
    sudo ufw allow 'Nginx Full'

    # set up the repo
    git clone git@github.com:zhangir-azerbayev/mathlib-semantic-search.git
    cd mathlib-semantic-search
    pip install -r requirements.txt
    touch .env
    ```

10. make an `.env` file and put values for
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`
    - `OPENAI_API_KEY`

12. Splat this in `/etc/systemd/system/mathlib-search.service`
    ```ini
    [Unit]
    Description=Gunicorn instance of mathlib-semantic-search
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/mathlib-semantic-search
    ExecStart=/home/ubuntu/.local/bin/gunicorn --workers 1 --bind unix:mathlib-search.sock -m 007 src.web:app --timeout 120

    [Install]
    WantedBy=multi-user.target
    ```
14. Put this in `/etc/nginx/sites-available/mathlib-search`
    ```conf
    server {
        listen 80;
        server_name mathlib-search.edayers.com;

        location / {
            include proxy_params;
            proxy_pass http://unix:/home/ubuntu/mathlib-semantic-search/mathlib-search.sock;
        }
    }
    ```
12. `sudo ln -s /etc/nginx/sites-available/mathlib-search /etc/nginx/sites-enabled`
15. This is a hack, go to `/etc/nginx/nginx.conf` and replace the user with `root`. I tried for like 3 hours to get this working with the `www-data` user and it just can't seem to read from `mathlib-search.sock` no matter what I tried. This is a security issue but at least it works.
13. start everything
   ```sh
   sudo systemctl enable --now mathlib-search
   sudo systemctl enable --now nginx
   ```

10. Make an elastic IP
11. Associate it to your EC2 instance.
12. Go to your DNS and add a new A-record for that.

[todo] add TLS