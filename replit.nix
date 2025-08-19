{ pkgs }: {
  deps = [
    pkgs.python312Full
    pkgs.replitPackages.prybar-python312
    pkgs.replitPackages.stderred
  ];
}
