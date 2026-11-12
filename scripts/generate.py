#!/usr/bin/env python3
"""Write themes/kanagawa-<variant>.toml from the shared palette.

Each scope takes the role that the Neovim plugin uses for the same thing.

Usage: scripts/generate.py [path/to/palette.json]   (default: ../.github/palette.json)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VARIANTS = ["wave", "dragon", "lotus"]

# Helix scope -> (fg role, bg role, modifiers). A role of None leaves it unset.
STYLES = {
    # Syntax
    "attribute": ("syn.constant", None, []),
    "type": ("syn.type", None, []),
    "type.builtin": ("syn.type", None, []),
    "type.enum.variant": ("syn.constant", None, []),
    "constructor": ("syn.special1", None, []),
    "constant": ("syn.constant", None, []),
    "constant.builtin.boolean": ("syn.constant", None, ["bold"]),
    "constant.numeric": ("syn.number", None, []),
    "constant.character": ("syn.string", None, []),
    "constant.character.escape": ("syn.regex", None, ["bold"]),
    "string": ("syn.string", None, []),
    "string.regexp": ("syn.regex", None, []),
    "string.special": ("syn.special1", None, []),
    "string.special.symbol": ("syn.identifier", None, []),
    "comment": ("syn.comment", None, ["italic"]),
    "variable": ("ui.fg", None, []),
    "variable.parameter": ("syn.parameter", None, []),
    "variable.builtin": ("syn.special2", None, ["italic"]),
    "variable.other.member": ("syn.identifier", None, []),
    "label": ("syn.special1", None, []),
    "punctuation": ("syn.punct", None, []),
    "punctuation.special": ("syn.special1", None, []),
    "keyword": ("syn.keyword", None, ["italic"]),
    "keyword.control": ("syn.statement", None, []),
    "keyword.control.import": ("syn.preproc", None, []),
    "keyword.control.return": ("syn.special3", None, ["italic"]),
    "keyword.control.exception": ("syn.special3", None, []),
    "keyword.directive": ("syn.preproc", None, []),
    "keyword.operator": ("syn.operator", None, ["bold"]),
    "operator": ("syn.operator", None, []),
    "function": ("syn.fun", None, []),
    "function.builtin": ("syn.special1", None, []),
    "function.macro": ("syn.preproc", None, []),
    "tag": ("syn.fun", None, []),
    "tag.attribute": ("syn.identifier", None, []),
    "namespace": ("syn.identifier", None, []),
    "special": ("syn.special1", None, []),
    "markup.heading": ("syn.fun", None, ["bold"]),
    "markup.list": ("syn.special1", None, []),
    "markup.list.unchecked": ("ui.nontext", None, []),
    "markup.list.checked": ("syn.string", None, []),
    "markup.bold": (None, None, ["bold"]),
    "markup.italic": (None, None, ["italic"]),
    "markup.strikethrough": (None, None, ["crossed_out"]),
    "markup.underline": (None, None, ["underlined"]),
    "markup.link.text": ("syn.fun", None, []),
    "markup.link.label": ("syn.fun", None, []),
    "markup.raw": ("syn.string", None, []),
    "markup.quote": ("syn.parameter", None, []),
    "diff.plus": ("vcs.added", None, []),
    "diff.minus": ("vcs.removed", None, []),
    "diff.delta": ("vcs.changed", None, []),
    # Interface
    "ui.background": ("ui.fg", "ui.bg", []),
    "ui.linenr": ("ui.nontext", None, []),
    "ui.linenr.selected": ("diag.warning", None, ["bold"]),
    "ui.statusline": ("ui.fg_dim", "ui.bg_m3", []),
    "ui.statusline.inactive": ("ui.nontext", "ui.bg_m3", []),
    "ui.statusline.normal": ("ui.bg", "syn.fun", ["bold"]),
    "ui.statusline.insert": ("ui.bg", "syn.string", ["bold"]),
    "ui.statusline.select": ("ui.bg", "syn.keyword", ["bold"]),
    "ui.popup": ("ui.float.fg", "ui.float.bg", []),
    "ui.help": ("ui.float.fg", "ui.float.bg", []),
    "ui.window": ("ui.bg_m3", None, []),
    "ui.bufferline": ("ui.fg_dim", "ui.bg_m3", []),
    "ui.bufferline.active": ("ui.fg", "ui.bg", ["bold"]),
    "ui.bufferline.background": (None, "ui.bg_m3", []),
    "ui.text": ("ui.fg", None, []),
    "ui.text.focus": ("ui.fg", "ui.bg_p2", ["bold"]),
    "ui.text.inactive": ("syn.comment", None, []),
    "ui.text.directory": ("syn.fun", None, []),
    "ui.virtual": ("ui.nontext", None, []),
    "ui.virtual.ruler": (None, "ui.bg_p1", []),
    "ui.virtual.indent-guide": ("ui.whitespace", None, []),
    "ui.virtual.inlay-hint": ("syn.comment", None, []),
    "ui.virtual.jump-label": ("syn.special3", None, ["bold"]),
    "ui.selection": (None, "ui.bg_visual", []),
    "ui.cursor": ("ui.bg", "ui.fg_dim", []),
    "ui.cursor.primary": ("ui.bg", "ui.fg", []),
    "ui.cursor.match": ("diag.warning", None, ["bold"]),
    "ui.cursorline.primary": (None, "ui.bg_p2", []),
    "ui.highlight": (None, "ui.bg_p2", []),
    "ui.menu": ("ui.pmenu.fg", "ui.pmenu.bg", []),
    "ui.menu.selected": ("ui.pmenu.fg", "ui.pmenu.bg_sel", ["bold"]),
    "ui.menu.scroll": ("ui.pmenu.bg_thumb", "ui.pmenu.bg_sbar", []),
    "diagnostic.unnecessary": (None, None, ["dim"]),
    "diagnostic.deprecated": (None, None, ["crossed_out"]),
    "error": ("diag.error", None, []),
    "warning": ("diag.warning", None, []),
    "info": ("diag.info", None, []),
    "hint": ("diag.hint", None, []),
}
# Scopes drawn with a curly underline in a role's color.
UNDERLINES = {
    "string.special.url": "syn.special1",
    "markup.link.url": "syn.special1",
    "diagnostic.error": "diag.error",
    "diagnostic.warning": "diag.warning",
    "diagnostic.info": "diag.info",
    "diagnostic.hint": "diag.hint",
}


def roles(variant):
    """Map each role to its hex color; a role missing from the palette raises KeyError later."""
    return {role: c["hex"] for c in variant["colors"].values() for role in c["usage"]}


def theme(variant, colors):
    out = [f"# Kanagawa {variant.capitalize()}", "# https://github.com/kanagawa-community/helix", ""]
    for scope, (fg, bg, mods) in STYLES.items():
        parts = [f'fg = "{colors[fg]}"'] if fg else []
        parts += [f'bg = "{colors[bg]}"'] if bg else []
        parts += ["modifiers = [" + ", ".join(f'"{m}"' for m in mods) + "]"] if mods else []
        out.append(f'"{scope}" = {{ {", ".join(parts)} }}')
    for scope, role in UNDERLINES.items():
        fg = f'fg = "{colors[role]}", ' if not scope.startswith("diagnostic") else ""
        out.append(f'"{scope}" = {{ {fg}underline = {{ color = "{colors[role]}", style = "curl" }} }}')
    return "\n".join(out) + "\n"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / ".github" / "palette.json"
    variants = json.loads(path.read_text())["variants"]
    for v in VARIANTS:
        out = ROOT / "themes" / f"kanagawa-{v}.toml"
        out.parent.mkdir(exist_ok=True)
        out.write_text(theme(v, roles(variants[v])))
        print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
