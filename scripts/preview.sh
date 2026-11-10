# Preview hook for .github/scripts/render-previews.sh: Helix runs in a headless
# tmux pane with each theme and opens this port's own generator, with a few
# lines selected, so syntax, selection, line numbers and the statusline show.
# Requires: helix, tmux.
# shellcheck shell=bash
name=helix

setup() {
  mkdir -p "$work/cfg/helix/themes" "$work/cache"
  cp "$root"/themes/*.toml "$work/cfg/helix/themes/"
}

cleanup() {
  tmux -L kanagawa-preview kill-server 2>/dev/null || true
}

capture() {
  cleanup
  printf 'theme = "kanagawa-%s"\n[editor]\nbufferline = "always"\ncolor-modes = true\n' "$1" >"$work/cfg/helix/config.toml"
  sleep 0.5
  tmux -L kanagawa-preview new-session -d -s s -x 100 -y 30 -c "$root" \
    -e XDG_CONFIG_HOME="$work/cfg" -e XDG_CACHE_HOME="$work/cache" \
    -e COLORTERM=truecolor -e TERM=xterm-256color -e LC_ALL=C.UTF-8 \
    "$(command -v helix || command -v hx) scripts/generate.py"
  sleep 1.5
  # Go to the STYLES table and select three lines.
  tmux -L kanagawa-preview send-keys -t s 28 g g x x x
  sleep 0.7
  tmux -L kanagawa-preview capture-pane -p -e -t s >"$2"
}
