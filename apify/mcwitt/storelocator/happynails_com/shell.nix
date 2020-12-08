{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  buildInputs = [ pkgs.zlib ];
  shellHook = with pkgs; ''
    export LD_LIBRARY_PATH=${lib.makeLibraryPath [ stdenv.cc.cc ]}
  '';
}
