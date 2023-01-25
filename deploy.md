This is what I did to set up a deployment instance on AWS.
I think eventually the answer is to make a docker image.

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



10. Make an elastic IP
11. Associate it to your EC2 instance.