# Learn Serverless Framew work in easy eay 
install external python packages on serverless

# Tutorials 


#### Lambda Event Bride and Serverless 
* Part 1: https://www.youtube.com/watch?v=Ke7DSpsszWY
* Part 2: https://www.youtube.com/watch?v=qVk1L7MHjGM&t=454s
* Part 3: https://www.youtube.com/watch?v=lC489CpKg-s
* Part 4 : https://www.youtube.com/watch?v=SEHEAVOMQfQ
* Part 4: https://www.youtube.com/watch?v=0Wb-a9Fa7pQ&t=77s
* Part 5: https://youtu.be/cLK-mFLYzvY
* Part 6: https://www.youtube.com/watch?v=UglcKQ3cnvc&list=PLL2hlSFBmWwzA7ut0KKYM6F8LKfu84-5c&index=7



#### Lambda Event Bride and Serverless 
* Serverless and API gateway and Lambda Hello World
* Lab 7: https://youtu.be/fPxos27jOFE





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
* https://aws.plainenglish.io/serverless-framework-setting-up-a-custom-domain-to-api-gateway-91064a598f1d


# Further reading 

* Build a Python REST API with Serverless, Lambda, and DynamoDB
https://www.serverless.com/blog/flask-python-rest-api-serverless-lambda-dynamodb/








