#!/bin/bash

create_user() {
  curl -XPOST 'http://localhost:5000/signup' \
    -H 'Content-Type: application/json' \
    --data '{"email":"'$1'","password":"'$2'","name":"foobar","surname":"foobar"}'
}

create_user "1" "a"
create_user "2" "a"
create_user "3" "a"
create_user "4" "a"

# create user
curl -XPOST 'http://localhost:5000/signup' \
  -H 'Content-Type: application/json' \
  --data '{"email":"email","password":"password","name":"foobar","surname":"foobar"}'

# login and get access token
access_token=$(curl -s -XPOST 'http://localhost:5000/login' \
  -H 'Content-Type: application/json' \
  --data '{"email":"email","password":"password"}' | jq -r '.access_token')

echo $access_token

curl -XGET 'http://localhost:5000/users' \
  -H "Authorization: Bearer $access_token" | jq