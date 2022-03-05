# install-external-python-packages-on-serverless
install external python packages on serverless



## Step 1: Install Serverless
```
npm install -g serverless

serverless config credentials --provider aws --key XXXX  --secret XXXXX -o

```


## Step 2: Create Project 
```
serverless create --template aws-python3 --name lambda-learn  --path lambda-learn

cd  lambda-learn
```


## Step 3: Install plugins
```
sls plugin install -n serverless-python-requirements

cd  lambda-learn
```

## Step 4:  
```
sls deploy
```


Reference

* https://www.serverless.com/blog/serverless-python-packaging/
  
* https://www.serverless.com/plugins/serverless-python-requirements


