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
      args=()
      yes=false
      for arg in "$@"; do
        case "$arg" in
          -y|--yes) yes=true ;;
          *) args+=("$arg") ;;
        esac
      done

      collections=$(mongosh lichess --quiet --eval 'db.getCollectionNames().length' 2>/dev/null || echo 0)
      if [ "$yes" != true ] && [ "$collections" -gt 0 ]; then
        echo "⚠️  Your local lichess database will be reset and any data will be lost."
        read -r -p "Continue? [y/N] " reply
        case "$reply" in
          [yY]|[yY][eE][sS]) ;;
          *) echo "Aborted."; exit 1 ;;
        esac
      fi

      ${python}/bin/python ${./spamdb}/spamdb.py \
        --drop-db \
        --streamers \
        --coaches \
        --tokens \
        "''${args[@]}"
      echo "Creating indexes..."
      indexes="$DEVENV_ROOT/bin/mongodb/indexes.js" # when imported by lila
      [ -f "$indexes" ] || indexes="''${LILA_PATH:-$DEVENV_ROOT/../lila}/bin/mongodb/indexes.js"
      mongosh lichess "$indexes"
      echo "✅ Done!"
    '';
  };
}
