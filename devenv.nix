{ pkgs, ... }:
let
  python = pkgs.python3.withPackages (ps: [
    ps.pymongo
    ps.requests
    ps.faker
    ps.chess
  ]);
in
{
  packages = [
    pkgs.mongosh
    pkgs.jre_headless # spamdb hashes passwords with lila_crypt.jar
    python
  ];

  scripts.seed = {
    exec = ''
      ${python}/bin/python ${./spamdb}/spamdb.py \
        --drop-db \
        --streamers \
        --coaches \
        --tokens \
        "$@"
      echo "Creating indexes..."
      indexes="$DEVENV_ROOT/bin/mongodb/indexes.js" # when imported by lila
      [ -f "$indexes" ] || indexes="''${LILA_PATH:-$DEVENV_ROOT/../lila}/bin/mongodb/indexes.js"
      mongosh lichess "$indexes"
      echo "✅ Done!"
    '';
  };
}
