"""Export the proposal and bibliography to an editable Word document (stdlib only)."""

from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", NS)


def tag(name):
    return "{" + NS + "}" + name


def paragraph(parent, text, style=None):
    p = ET.SubElement(parent, tag("p"))
    if style:
        props = ET.SubElement(p, tag("pPr"))
        ET.SubElement(props, tag("pStyle"), {tag("val"): style})
    run = ET.SubElement(p, tag("r"))
    node = ET.SubElement(run, tag("t"))
    node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    node.text = text


def clean(text):
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.replace("**", "").replace("`", "")


def export(paths, output):
    document = ET.Element(tag("document"))
    body = ET.SubElement(document, tag("body"))
    paragraph(body, "León en el tiempo", "Title")
    paragraph(
        body, "Propuesta de investigación aplicada y prototipo educativo · UNI · 2026"
    )
    paragraph(
        body,
        "Primera entrega. Investigación documental inicial; evaluación con usuarios pendiente. Los nombres del equipo, docente y fecha de entrega deben completarse por el estudiante.",
    )
    for path in paths:
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("|"):
                cells = [clean(x.strip()) for x in line.strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", x) for x in cells):
                    rows.append(cells)
                continue
            if rows:
                table = ET.SubElement(body, tag("tbl"))
                props = ET.SubElement(table, tag("tblPr"))
                ET.SubElement(props, tag("tblStyle"), {tag("val"): "TableGrid"})
                for cells in rows:
                    tr = ET.SubElement(table, tag("tr"))
                    for cell in cells:
                        tc = ET.SubElement(tr, tag("tc"))
                        paragraph(tc, cell)
                rows = []
            if not line.strip():
                continue
            match = re.match(r"^(#{1,3})\s+(.*)", line)
            if match:
                paragraph(
                    body, clean(match.group(2)), "Heading" + str(len(match.group(1)))
                )
            else:
                paragraph(body, clean(line))
        if rows:
            for row in rows:
                paragraph(body, " | ".join(row))
    section = ET.SubElement(body, tag("sectPr"))
    ET.SubElement(section, tag("pgSz"), {tag("w"): "11906", tag("h"): "16838"})
    ET.SubElement(
        section,
        tag("pgMar"),
        {
            tag("top"): "1440",
            tag("right"): "1440",
            tag("bottom"): "1440",
            tag("left"): "1440",
        },
    )
    content_types = """<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    doc_rels = """<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>"""
    styles = ET.Element(tag("styles"))
    for name, size in [
        ("Normal", 22),
        ("Title", 40),
        ("Heading1", 32),
        ("Heading2", 28),
        ("Heading3", 24),
    ]:
        style = ET.SubElement(
            styles, tag("style"), {tag("type"): "paragraph", tag("styleId"): name}
        )
        ET.SubElement(style, tag("name"), {tag("val"): name})
        props = ET.SubElement(style, tag("rPr"))
        ET.SubElement(props, tag("sz"), {tag("val"): str(size)})
        if name != "Normal":
            ET.SubElement(props, tag("b"))
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr(
            "word/document.xml",
            ET.tostring(document, encoding="utf-8", xml_declaration=True),
        )
        z.writestr(
            "word/styles.xml",
            ET.tostring(styles, encoding="utf-8", xml_declaration=True),
        )
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        ET.fromstring(z.read("word/document.xml"))
    print(output)


if __name__ == "__main__":
    export(
        [
            ROOT / "docs/propuesta.md",
            ROOT / "docs/fuentes.md",
            ROOT / "docs/evidencias.md",
        ],
        ROOT / "docs/Leon-en-el-tiempo-propuesta.docx",
    )
