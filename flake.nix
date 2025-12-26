{
  description = "CamdenTools DB Backend dev shell (flake)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      forAllSystems = nixpkgs.lib.genAttrs systems;

      mkDevShell = pkgs:
        let
          php = pkgs.php84.buildEnv {
            extensions = ({ enabled, all }: with all; [
              bcmath
              calendar
              ctype
              curl
              dom
              exif
              fileinfo
              filter
              ftp
              gd
              gettext
              iconv
              igbinary
              imagick
              imap
              intl
              mbstring
              mysqli
              openssl
              pcntl
              pdo
              pdo_mysql
              pdo_pgsql
              pgsql
              posix
              readline
              redis
              session
              shmop
              simplexml
              sockets
              sodium
              tokenizer
              xmlreader
              xmlwriter
              xsl
              opcache
              zip
              zlib
            ]);
            extraConfig = ''
              memory_limit = -1
              max_execution_time = 0
              post_max_size = 2048M
              upload_max_filesize = 2048M
            '';
          };
        in
        pkgs.mkShell {
          buildInputs = [
            php
            pkgs.php84Packages.composer
            pkgs.redis
            pkgs.nodejs_20
            pkgs.bun
            pkgs.meilisearch
          ];

          shellHook = ''
            echo "nix ---------- by 93foxy"
            echo "Quick start:"
            echo "  php artisan serve"
            echo ""
            echo "Services:"
            echo "  nix-shell --run \"redis-server\" # Start Redis server"
            echo "nix ----------"
          '';
        };
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = mkDevShell pkgs;
        });
    };
}
