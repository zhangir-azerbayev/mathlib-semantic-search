This is what I did to set up a deployment instance on AWS.
I think eventually the answer is to make a docker image.

1. Set up an EC2 instance.
2. `sudo yum update -y`
3. `sudo yum install git -y`
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
7. `pyenv install 3.10.9`


# Elastic beanstalk

Created `.ebignore`

```
eb init
```

1.