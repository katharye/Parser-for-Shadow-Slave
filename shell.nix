# { pkgs ? import <nixpkgs> {} }:
# 
# pkgs.mkShell {
# 
#   packages = with pkgs; [
#     python313
#     python313Packages.pip
#     python313Packages.setuptools
#     python313Packages.wheel
# 
#     rustc
#     cargo
# 
#     pkg-config
#     openssl
#     libffi
#     libxml2
#     libxslt
#     zlib
#   ];
# 
#   env = {
#     LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
#       pkgs.stdenv.cc.cc.lib
#       pkgs.zlib
#       pkgs.libxml2
#       pkgs.libxslt
#     ];
# 
#     PKG_CONFIG_PATH = pkgs.lib.makeSearchPath "lib/pkgconfig" [
#       pkgs.libxml2
#       pkgs.libxslt
#     ];
#   };
# 
#     shellHook = ''
#         if [ ! -d ".venv" ]; then
#             echo "Creating virtual environment .venv..."
#             python -m venv .venv
#         fi
# 
#         source .venv/bin/activate
#         echo "popa"
#     '';
#     # TIPS:
# 
#         # pip install ...
#         # pip freeze > reauirments.txt
# }

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    python313
    python313Packages.pip
    python313Packages.setuptools
    python313Packages.wheel

    rustc
    cargo

    pkg-config
    openssl
    libffi
    libxml2
    libxslt
    zlib
  ];

  shellHook = ''
    if [ -z "$VIRTUAL_ENV" ]; then
      if [ ! -d ".venv" ]; then
        echo "Creating Python virtual environment (.venv)..."
        python -m venv .venv
      fi

      source .venv/bin/activate
    fi

    export PKG_CONFIG_PATH=${pkgs.lib.makeSearchPath "lib/pkgconfig" [
      pkgs.openssl
      pkgs.libffi
      pkgs.libxml2
      pkgs.libxslt
    ]}
  '';
}
