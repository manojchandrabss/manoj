#!/bin/bash

if [ ! -f .install ]; then
  # Install dependenices for UI CLI
  sudo npm install -g jshint
  sudo npm install -g grunt-cli
  sudo npm install -g grunt
  sudo npm install -g bower
  sudo npm install -g eslint
  sudo npm install -g js-beautify
  sudo npm install -g javascript-ctags
  sudo npm install -g handlebars
  sudo npm install -g apidoc
  sudo npm install -g marked
  sudo npm install -g jsonlint
  sudo pip install checksumdir
  sudo pip install flake8
  python -mplatform | grep Ubuntu && sudo apt-get -y install cowsay || sudo dnf install -y cowsay
  ctags -R apps/ libs/ assets/js/* templates TAGS
  echo `date` >> .install
fi

# Install bower deps
bower install

# Install node deps
npm install

