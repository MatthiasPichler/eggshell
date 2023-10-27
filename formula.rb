class Eggshell < Formula
  desc "A GTP powered CLI"
  homepage "https://github.com/MatthiasPichler/eggshell"
  url "https://github.com/MatthiasPichler/eggshell"
  sha256 "checksum-here"

  depends_on "python"

  def install
    bin.install "eggshell.sh"
  end
end
