provider "heroku" {
}


resource "heroku_app" "servers" {
  name   = "servers-terraform"
  region = "eu"
  stack  = "container"
}


resource "heroku_addon" "database" {
  app_id  = heroku_app.servers.id
  plan = "heroku-postgresql:hobby-dev"
}