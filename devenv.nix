{ ... }:
{
  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = ./spamdb/requirements.txt;
    };
  };
}
