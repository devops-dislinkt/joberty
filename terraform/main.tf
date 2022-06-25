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
  name   =  "name"
  region = "eu"
  stack  = "container"
}



resource "heroku_build" "servers" {
  app_id = heroku_app.servers.id

  source {
    path = "servers"
  }
}


