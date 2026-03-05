{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.flask
    pkgs.gcc
    pkgs.octaveFull
    pkgs.gnuplot  # <--- AJOUTE CETTE LIGNE ICI
  ];
}