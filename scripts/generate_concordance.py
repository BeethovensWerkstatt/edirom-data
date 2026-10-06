#!/usr/bin/env python3
"""
Erzeugt Taktkonkordanzen für ein Werk in edition/edition.xml.

Takte werden über das Satz-Label (mdiv/@label) und das Takt-Label
(measure/@label, ersatzweise @n) quellenübergreifend verbunden.
Für jede Leitquelle entsteht eine <concordance> "Taktnavigation nach: …",
deren Sätze und Takte in der Reihenfolge dieser Quelle stehen.

Takte mit Label "x" (z. B. gestrichene Takte) werden ausgelassen.
Kommagetrennte Labels ("12,13") verbinden einen Takt mit mehreren Taktnummern.

Beispiel:
    python3 scripts/generate_concordance.py --work op120_work --dir op120 \
        --source "Ausgangsdokument=Ausgangsdokument.xml" \
        --source "Originalausgabe=Originalausgabe.xml" \
        --source "Zieldokument=Zieldokument.xml"
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

MEI = '{http://www.music-encoding.org/ns/mei}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
DB_PREFIX = 'xmldb:exist:///db/apps/beethoven-edirom-data'
SKIP_LABELS = {'x'}

ROOT = Path(__file__).resolve().parent.parent
EDITION = ROOT / 'edition'


def read_source(path):
    """Liefert [(mdiv_label, [(measure_label, measure_id), ...]), ...] in Dokumentreihenfolge."""
    root = ET.parse(path).getroot()
    result = []
    for mdiv in root.iter(MEI + 'mdiv'):
        measures = []
        for m in mdiv.iter(MEI + 'measure'):
            label = m.get('label') or m.get('n')
            if label is None or label in SKIP_LABELS:
                continue
            # "12,13": ein Takt, der zwei Takten anderer Quellen entspricht
            for part in label.split(','):
                measures.append((part.strip(), m.get(XML_ID)))
        result.append((mdiv.get('label') or mdiv.get('n'), measures))
    return result


def build_concordances(sources, work_dir, indent='            '):
    # index: (mdiv_label, measure_label) -> [uri, ...] über alle Quellen
    index = {}
    for _, filename, data in sources:
        uri = f'{DB_PREFIX}/{work_dir}/{filename}'
        for mdiv_label, measures in data:
            for label, mid in measures:
                index.setdefault((mdiv_label, label), []).append(f'{uri}#{mid}')

    def names(text, ind):
        # Edirom Online ab 1.x liest Namen aus <names>, ältere Versionen aus @name/@label
        return [f'{ind}<names>', f'{ind}    <name xml:lang="de">{escape(text)}</name>', f'{ind}</names>']

    i = indent
    out = [f'{i}<concordances>']
    for name, _, data in sources:
        title = 'Taktnavigation nach: ' + name
        out.append(f'{i}    <concordance name={quoteattr(title)}>')
        out += names(title, f'{i}        ')
        out.append(f'{i}        <groups label="Satz">')
        out += names('Satz', f'{i}            ')
        for mdiv_label, measures in data:
            out.append(f'{i}            <group name={quoteattr(mdiv_label)}>')
            out += names(mdiv_label, f'{i}                ')
            labels = list(dict.fromkeys(label for label, _ in measures))
            if not labels:
                out.append(f'{i}                <connections label="Takt"/>')
            else:
                out.append(f'{i}                <connections label="Takt">')
                for label in labels:
                    plist = ' '.join(index[(mdiv_label, label)])
                    out.append(f'{i}                    <connection name={quoteattr(label)} plist={quoteattr(plist)}/>')
                out.append(f'{i}                </connections>')
            out.append(f'{i}            </group>')
        out.append(f'{i}        </groups>')
        out.append(f'{i}    </concordance>')
    out.append(f'{i}</concordances>')
    return '\n'.join(out)


def replace_in_edition(edition_xml, work_id, concordances):
    text = edition_xml.read_text(encoding='utf-8')
    start = text.find(f'<work xml:id="{work_id}"')
    if start < 0:
        sys.exit(f'Werk {work_id} nicht in {edition_xml} gefunden')
    end = text.index('</work>', start)
    work = text[start:end]
    pattern = re.compile(r'[ \t]*<concordances\s*/>|[ \t]*<concordances>.*?</concordances>', re.S)
    if not pattern.search(work):
        sys.exit(f'Kein <concordances> in Werk {work_id}')
    work = pattern.sub(lambda _: concordances, work, count=1)
    edition_xml.write_text(text[:start] + work + text[end:], encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', required=True, help='xml:id des <work> in edition.xml')
    ap.add_argument('--dir', required=True, help='Unterordner des Werks in edition/, z. B. op120')
    ap.add_argument('--source', action='append', required=True, metavar='NAME=DATEI',
                    help='Leitquelle (Anzeigename=Dateiname im Werkordner); mehrfach angeben')
    ap.add_argument('--dry-run', action='store_true', help='Nur ausgeben, edition.xml nicht ändern')
    args = ap.parse_args()

    sources = []
    for spec in args.source:
        name, filename = spec.split('=', 1)
        sources.append((name, filename, read_source(EDITION / args.dir / filename)))

    concordances = build_concordances(sources, args.dir)
    if args.dry_run:
        print(concordances)
    else:
        replace_in_edition(EDITION / 'edition.xml', args.work, concordances)
        print(f'Konkordanzen für {args.work} geschrieben.')

    # Bericht: Takte, die nicht in allen Quellen vorkommen
    keys = [{(md, l) for md, ms in data for l, _ in ms} for _, _, data in sources]
    for (name, _, _), own in zip(sources, keys):
        missing = sorted(set().union(*keys) - own)
        if missing:
            print(f'  {name}: {len(missing)} Takt-Labels fehlen gegenüber den anderen Quellen', file=sys.stderr)


if __name__ == '__main__':
    main()
