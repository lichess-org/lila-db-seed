{ pkgs, ... }:
{
  packages = [
    pkgs.mongosh
  ];

  languages.python = {
    enable = true;
    venv = {
      enable = true;
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
