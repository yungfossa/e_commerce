access_token="$1"

list_category() {
  curl -g -s -XGET 'http://localhost:5000/admin/category' \
    -H "Authorization: Bearer $access_token"
}

create_category () {
  curl -g -s -XPUT 'http://localhost:5000/admin/category' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $access_token" \
    -d '{"category_title": "'$1'"}' | jq
}

delete_category () {
  curl -g -s -XDELETE 'http://localhost:5000/admin/category' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $access_token" \
    -d '{"category_title": "'$1'"}' | jq
}

create_product () {
  curl -g -s -XPUT 'http://localhost:5000/admin/products' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $access_token" \
    -d '{
      "name": "'$1'",
      "description": "'$2'",
      "image_src": "'$3'",
      "category": "'$4'"
    }' | jq
}

list_product () {
  curl -g -s -XPOST 'http://localhost:5000/admin/products' \
    -H 'Content-Type: application/json' \
    -d '{
      "limit": 50,
      "offset": 0
    }' | jq
}


create_category "Misc"
create_category "Tool"
delete_category "Tool"
list_category

# create_product "Mouse" "Logitech Mouse" "google.com" "Tech"

# curl -g -s -XPUT 'http://localhost:5000/product' \
#   -H 'Content-Type: application/json' \
#   -H "Authorization: Bearer $access_token" \
#   -d '{
#     "name": "Mouse",
#     "description": "Logitech",
#     "image_src": "google.com",
#     "category": "Tech"
#   }' | jq
#
# list_product
