#!/usr/bin/env python3
"""
Ergänzt Konkordanzen in edition/edition.xml um <names>-Elemente.

Edirom Online ab 1.x liest die Namen von <concordance>, <groups> und <group>
aus <names><name xml:lang="…">…</name></names>; die alten Attribute
@name/@label bleiben für ältere Versionen erhalten.

Konkordanzen nach den Kommentaren <!-- ante --> bzw. <!-- post -->
erhalten den Zusatz "(ante revisionem)" bzw. "(post revisionem)".

Das Skript ist idempotent: bereits vorhandene <names> werden nicht verdoppelt.
"""
import re
from pathlib import Path
from xml.sax.saxutils import escape, unescape

EDITION_XML = Path(__file__).resolve().parent.parent / 'edition' / 'edition.xml'
SUFFIX = {'ante': ' (ante revisionem)', 'post': ' (post revisionem)'}

TAG = re.compile(
    r'(?P<comment><!--\s*(?P<marker>ante|post|[^-]*?)\s*-->)'
    r'|(?P<indent>[ \t]*)(?P<tag><(?P<el>concordance|groups|group)\b[^>]*?(?:name|label)="(?P<value>[^"]*)"[^>]*>)'
    r'(?P<names>\s*<names>)?'
)


def names_block(text, indent):
    return (f'\n{indent}    <names>\n'
            f'{indent}        <name xml:lang="de">{escape(text)}</name>\n'
            f'{indent}    </names>')


def main():
    xml = EDITION_XML.read_text(encoding='utf-8')
    suffix = ''

    def repl(m):
        nonlocal suffix
        if m.group('comment'):
            marker = m.group('marker').strip()
            if marker in SUFFIX:
                suffix = SUFFIX[marker]
            elif marker == 'Autograph':
                suffix = ''
            return m.group(0)
        if m.group('names'):
            return m.group(0)
        text = unescape(m.group('value'))
        if m.group('el') == 'concordance':
            text += suffix
        return m.group('indent') + m.group('tag') + names_block(text, m.group('indent'))

    # Zusatz nur innerhalb des Werks, in dem die Kommentare stehen
    out, pos = [], 0
    for work in re.finditer(r'<work\b.*?</work>', xml, re.S):
        out.append(xml[pos:work.start()])
        suffix = ''
        out.append(TAG.sub(repl, work.group(0)))
        pos = work.end()
    out.append(xml[pos:])
    EDITION_XML.write_text(''.join(out), encoding='utf-8')


if __name__ == '__main__':
    main()
