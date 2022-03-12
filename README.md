# Learn Serverless Framew work in easy eay 
install external python packages on serverless

# Tutorials 
* Part 1: https://www.youtube.com/watch?v=Ke7DSpsszWY
* Part 2: https://www.youtube.com/watch?v=qVk1L7MHjGM&t=454s
* Part 3: https://www.youtube.com/watch?v=lC489CpKg-s
* Part 4 : https://www.youtube.com/watch?v=SEHEAVOMQfQ
* Part 4: https://www.youtube.com/watch?v=0Wb-a9Fa7pQ&t=77s
* Part 5: https://youtu.be/cLK-mFLYzvY



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


### Reference

* https://www.serverless.com/blog/serverless-python-packaging/
  
* https://www.serverless.com/plugins/serverless-python-requirements

* https://towardsdatascience.com/deploying-aws-lamba-function-layer-with-serverless-framework-f3f4fab1b7e9

# Further reading 

* Build a Python REST API with Serverless, Lambda, and DynamoDB
https://www.serverless.com/blog/flask-python-rest-api-serverless-lambda-dynamodb/





