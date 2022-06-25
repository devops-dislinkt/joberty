terraform {
  required_providers {
    heroku = {
      source = "heroku/heroku"
      version = "5.1.0"
    }
  }
}

provider "heroku" {
  # Configuration options
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