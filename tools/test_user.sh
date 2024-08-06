#!/bin/bash

create_user() {
  curl -s -XPOST 'http://localhost:5000/signup' \
    -H 'Content-Type: application/json' \
    --data '{"email":"'"$1"'","password":"'"$2"'","name":"foobar","surname":"foobar"}'
}

# function to log in, access /profile route, and log out
login_access_and_logout() {
  local email=$1
  local password=$2

  # login and get access token
  access_token=$(curl -s -XPOST 'http://localhost:5000/login' \
    -H 'Content-Type: application/json' \
    --data '{"email":"'"$email"'","password":"'"$password"'"}' | jq -r '.data.access_token')

  echo "Access Token for $email: $access_token"

  # access /profile route
  echo "Accessing profile for $email:"
  curl -s -XGET 'http://localhost:5000/profile' \
    -H "Authorization: Bearer $access_token" | jq

  # access /cart route
  echo "Accessing cart for $email:"
  curl -s -XGET 'http://localhost:5000/cart' \
    -H "Authorization: Bearer $access_token" | jq

  # logout
  logout_response=$(curl -s -XDELETE 'http://localhost:5000/logout' \
    -H "Authorization: Bearer $access_token")

  echo "Logout response for $email: $logout_response"
}

# create sample users
create_user "email123@example.com" "password"

# login, access /profile, and logout for each created user
#  login_access_and_logout "email@example.com" "password"
