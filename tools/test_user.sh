#!/bin/bash

# create user
curl -XPOST 'http://localhost:5000/signup' \
  -H 'Content-Type: application/json' \
  --data '{"email":"email","password":"password","name":"foobar","surname":"foobar"}'

# login and get access token
access_token=$(curl -XPOST 'http://localhost:5000/login' \
  -H 'Content-Type: application/json' \
  --data '{"email":"email","password":"password"}' | jq -r '.access_token')

echo $access_token

curl -XGET 'http://localhost:5000/protected' \
  -H "Authorization: Bearer $access_token"