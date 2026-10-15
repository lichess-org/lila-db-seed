{ pkgs, ... }:
{
  packages = [
    pkgs.mongosh
    pkgs.jre_headless # spamdb hashes passwords with lila_crypt.jar
  ];

  languages.python = {
    enable = true;
    directory = "./spamdb";
    venv = {
      enable = true;
      quiet = false;
      requirements = ./spamdb/requirements.txt;
    };
  };

  env.LILA_PATH = "../lila";

  scripts.seed = {
    exec = ''
      python spamdb/spamdb.py \
        --drop-db \
        --streamers \
        --coaches \
        --tokens
      echo "Creating indexes..."
      mongosh lichess $LILA_PATH/bin/mongodb/indexes.js
      echo "✅ Done!"
    '';
  };
}
