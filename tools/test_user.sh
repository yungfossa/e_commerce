#!/bin/bash

create_user() {
  curl -XPOST 'http://localhost:5000/signup' \
    -H 'Content-Type: application/json' \
    --data '{"email":"'$1'","password":"'$2'","name":"foobar","surname":"foobar"}'
}

# create sample users
create_user "1" "a"
create_user "2" "a"
create_user "3" "a"
create_user "4" "a"

# create a specific user
curl -XPOST 'http://localhost:5000/signup' \
  -H 'Content-Type: application/json' \
  --data '{"email":"email@example.com","password":"password","name":"foobar","surname":"foobar"}'

# function to log in and access /me route
login_and_access_me() {
  local email=$1
  local password=$2
  
  # login and get access token
  access_token=$(curl -s -XPOST 'http://localhost:5000/login' \
    -H 'Content-Type: application/json' \
    --data '{"email":"'$email'","password":"'$password'"}' | jq -r '.data.access_token')

  echo "Access Token for $email: $access_token"

  # access /me route
  curl -XGET 'http://localhost:5000/me' \
    -H "Authorization: Bearer $access_token" | jq
}

# login and access /me for each created user
login_and_access_me "1" "a"
login_and_access_me "2" "a"
login_and_access_me "3" "a"
login_and_access_me "4" "a"

# check users
curl -XGET 'http://localhost:5000/users' \
  -H "Authorization: Bearer $access_token" | jq