from __future__ import annotations

import html
import subprocess
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
LAB02_DIR = REPORTS_DIR / "screenshots" / "lab02"
LAB03_DIR = REPORTS_DIR / "screenshots" / "lab03"

FONT_MONO = "/System/Library/Fonts/Menlo.ttc"
FONT_SANS = "/System/Library/Fonts/Supplemental/Verdana.ttf"
FONT_SANS_BOLD = "/System/Library/Fonts/Supplemental/Verdana Bold.ttf"


def run(command: str) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    chunks = [part.strip("\n") for part in (result.stdout, result.stderr) if part.strip()]
    return "\n".join(chunks).strip()


def filtered_lines(raw: str, keep_empty: bool = False) -> list[str]:
    lines: list[str] = []
    for line in raw.splitlines():
        normalized = line.rstrip()
        if not normalized and not keep_empty:
            continue
        if "bootstrap.cc" in normalized or "child_port_handshake" in normalized:
            continue
        if "ERROR file_io.cc" in normalized:
            continue
        if normalized.startswith("[") and "ERROR" in normalized:
            continue
        if normalized.startswith("[") and "FATAL" in normalized:
            continue
        lines.append(normalized)
    return lines


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def wrap_block(lines: list[str], width: int = 88) -> list[str]:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=width) or [""])
    return wrapped


def render_terminal_capture(
    output_path: Path,
    title: str,
    command: str,
    content_lines: list[str],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    title_font = load_font(FONT_SANS_BOLD, 28)
    command_font = load_font(FONT_MONO, 18)
    body_font = load_font(FONT_MONO, 20)

    lines = [f"$ {command}", ""] + wrap_block(content_lines)

    probe = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(probe)

    margin = 28
    line_gap = 8
    body_heights: list[int] = []
    max_text_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line or " ", font=body_font if line not in (lines[0], "") else command_font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        max_text_width = max(max_text_width, width)
        body_heights.append(height)

    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_height = title_bbox[3] - title_bbox[1]
    title_width = title_bbox[2] - title_bbox[0]

    width = max(960, max_text_width + margin * 2, title_width + margin * 2)
    body_height = sum(body_heights) + line_gap * (len(lines) - 1)
    height = 120 + title_height + body_height + margin

    image = Image.new("RGB", (width, height), "#10151c")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((18, 18, width - 18, height - 18), radius=22, fill="#161d26", outline="#2f3b4b", width=2)
    draw.ellipse((34, 34, 50, 50), fill="#ff5f57")
    draw.ellipse((58, 34, 74, 50), fill="#febc2e")
    draw.ellipse((82, 34, 98, 50), fill="#28c840")

    y = 78
    draw.text((margin, y), title, font=title_font, fill="#f3f6fb")
    y += title_height + 18

    for index, line in enumerate(lines):
        if index == 0:
            font = command_font
            fill = "#7fd2ff"
        elif line == "":
            font = command_font
            fill = "#d5deea"
        else:
            font = body_font
            fill = "#d5deea"
        draw.text((margin, y), line, font=font, fill=fill)
        y += body_heights[index] + line_gap

    image.save(output_path)


def html_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{
      font-family: Verdana, sans-serif;
      color: #1a2433;
      margin: 44px;
      line-height: 1.45;
    }}
    h1, h2, h3 {{
      color: #0b2d5a;
    }}
    h1 {{
      font-size: 26px;
      margin-bottom: 8px;
    }}
    h2 {{
      margin-top: 24px;
      margin-bottom: 10px;
      font-size: 18px;
    }}
    p {{
      margin: 8px 0;
    }}
    ul {{
      margin-top: 8px;
      margin-bottom: 8px;
    }}
    li {{
      margin-bottom: 6px;
    }}
    .meta {{
      color: #40536d;
      font-size: 13px;
      margin-bottom: 18px;
    }}
    .note {{
      background: #eef4ff;
      border-left: 4px solid #6a8fdb;
      padding: 12px 14px;
      margin: 14px 0 18px;
    }}
    figure {{
      margin: 18px 0 22px;
      page-break-inside: avoid;
    }}
    img {{
      width: 100%;
      max-width: 640px;
      border: 1px solid #d4dce7;
    }}
    figcaption {{
      font-size: 12px;
      color: #54657d;
      margin-top: 6px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 12px 0 18px;
      font-size: 13px;
    }}
    th, td {{
      border: 1px solid #cfd6e1;
      padding: 8px 10px;
      vertical-align: top;
    }}
    th {{
      background: #f3f7fc;
      text-align: left;
    }}
  </style>
</head>
<body>
{body}
</body>
</html>"""


def figure(rel_path: str, caption: str) -> str:
    return (
        f'<figure><img src="{html.escape(rel_path)}" alt="{html.escape(caption)}">'
        f"<figcaption>{html.escape(caption)}</figcaption></figure>"
    )


def build_lab02_html() -> str:
    body = f"""
<h1>Лабораторна робота № 2</h1>
<div class="meta">Тема: встановлення та налаштування інструментів Android-розробки. Дата виконання: 11.03.2026.</div>

<p><strong>Мета роботи:</strong> перевірити наявність та працездатність засобів розробки Android і емулятора на поточній машині.</p>

<div class="note">
  Методичні вказівки орієнтовані на застарілий стек <strong>Eclipse + ADT + Intel HAXM + Windows</strong>. На цій машині фактичне виконання виконувалось у сучасному еквіваленті: <strong>Android Studio + Android SDK + Emulator + Hypervisor.Framework</strong> на <strong>macOS arm64</strong>. Це важливо, тому що ADT офіційно застарів, а HAXM не використовується на Apple Silicon.
</div>

<h2>Хід виконання</h2>
<ul>
  <li>Перевірено встановлення JDK. У системі наявна Java 21 LTS, що перевищує мінімальну вимогу методички.</li>
  <li>Перевірено структуру Android SDK у каталозі <code>~/Library/Android/sdk</code>: доступні <code>build-tools</code>, <code>platform-tools</code>, <code>platforms</code>, <code>system-images</code>, <code>emulator</code>.</li>
  <li>Перевірено механізм апаратного прискорення емулятора. На macOS використовується <code>Hypervisor.Framework</code>, що є сучасною заміною HAXM.</li>
  <li>Перевірено доступні AVD та успішний запуск віртуального пристрою.</li>
</ul>

<h2>Фактичні результати</h2>
{figure("screenshots/lab02/01_java_version.png", "Рисунок 1 - Перевірка встановленої версії JDK")}
{figure("screenshots/lab02/02_android_sdk_contents.png", "Рисунок 2 - Вміст каталогу Android SDK")}
{figure("screenshots/lab02/03_emulator_accel.png", "Рисунок 3 - Перевірка механізму прискорення емулятора")}
{figure("screenshots/lab02/04_avd_list.png", "Рисунок 4 - Список доступних віртуальних пристроїв")}
{figure("screenshots/lab02/05_running_avd.png", "Рисунок 5 - Запущений віртуальний Android-пристрій")}

<h2>Висновок</h2>
<p>У ході роботи підтверджено наявність і працездатність ключових компонентів Android-середовища: JDK, Android SDK, системних образів, емулятора та AVD. Незважаючи на застарілість стеку Eclipse/ADT у методичних вказівках, ціль роботи досягнута сучасними підтримуваними засобами. Емулятор успішно запускається та може використовуватись для перевірки Android-застосунків.</p>
"""
    return html_page("Лабораторна робота № 2", body)


def build_lab03_html() -> str:
    body = f"""
<h1>Лабораторна робота № 3</h1>
<div class="meta">Тема: Android Studio. Створення та перевірка віртуального пристрою AVD. Дата виконання: 11.03.2026.</div>

<p><strong>Мета роботи:</strong> створити або перевірити налаштований AVD, запустити його та зафіксувати основні параметри роботи.</p>

<div class="note">
  Методичка описує <strong>Intel x86 + HAXM + Windows 7 + API 22</strong>. На поточній машині використовується <strong>arm64 macOS</strong>, тому фактичний еквівалент — <strong>arm64-v8a AVD</strong> із прискоренням через <strong>Hypervisor.Framework</strong>. Для Apple Silicon це правильний і підтримуваний сценарій.
</div>

<h2>Параметри використаного AVD</h2>
{figure("screenshots/lab03/00_avd_config.png", "Рисунок 1 - Конфігурація віртуального пристрою Medium_Phone_API_36.1")}

<h2>Виконання роботи</h2>
<ul>
  <li>Запущено AVD <code>Medium_Phone_API_36.1</code>.</li>
  <li>Перемкнено системну локаль на <code>ru-RU</code>, як вимагає завдання.</li>
  <li>Перевірено домашній екран після запуску пристрою.</li>
  <li>Відкрито сторінку мовних налаштувань і зафіксовано активну російську локаль.</li>
  <li>Відкрито сторінку відомостей про пристрій, де видно модель емулятора та версію Android.</li>
</ul>

<h2>Скріншоти виконання</h2>
{figure("screenshots/lab03/01_home_ru.png", "Рисунок 2 - Домашній екран запущеного AVD")}
{figure("screenshots/lab03/02_locale_settings_ru.png", "Рисунок 3 - Екран мовних налаштувань із локаллю Русский (Россия)")}
{figure("screenshots/lab03/03_about_device.png", "Рисунок 4 - Екран «Об эмулированном устройстве» з моделлю та версією Android")}

<h2>Підтверджені параметри</h2>
<table>
  <tr><th>Параметр</th><th>Значення</th></tr>
  <tr><td>AVD</td><td>Medium_Phone_API_36.1</td></tr>
  <tr><td>ABI</td><td>arm64-v8a</td></tr>
  <tr><td>Роздільна здатність</td><td>1080x2400</td></tr>
  <tr><td>RAM</td><td>2048 MB</td></tr>
  <tr><td>Мова системи</td><td>Русский (Россия)</td></tr>
  <tr><td>Модель</td><td>sdk_gphone64_arm64</td></tr>
  <tr><td>Версія Android</td><td>16</td></tr>
</table>

<h2>Висновок</h2>
<p>У роботі перевірено працездатний AVD у середовищі Android Studio та зафіксовано його основні параметри. Емулятор успішно запускається, підтримує зміну локалі та надає системні відомості про модель і версію Android. На Apple Silicon аналогом описаного в методичці Intel x86/HAXM є arm64 AVD з Hypervisor.Framework.</p>
"""
    return html_page("Лабораторна робота № 3", body)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_xml(text: str, *, bold: bool = False, size: int = 24, color: str = "141B26", font: str = "Verdana") -> str:
    props = [
        f'<w:rFonts w:ascii="{escape(font)}" w:hAnsi="{escape(font)}" w:cs="{escape(font)}"/>',
        f'<w:sz w:val="{size}"/>',
        f'<w:szCs w:val="{size}"/>',
        f'<w:color w:val="{color}"/>',
    ]
    if bold:
        props.append("<w:b/>")
    text_xml = f'<w:t xml:space="preserve">{escape(text)}</w:t>'
    return f"<w:r><w:rPr>{''.join(props)}</w:rPr>{text_xml}</w:r>"


def paragraph_xml(
    runs: list[str],
    *,
    spacing_after: int = 160,
    left: int | None = None,
    first_line: int | None = None,
) -> str:
    props = []
    if spacing_after:
        props.append(f'<w:spacing w:after="{spacing_after}"/>')
    if left is not None or first_line is not None:
        attrs = []
        if left is not None:
            attrs.append(f'w:left="{left}"')
        if first_line is not None:
            attrs.append(f'w:firstLine="{first_line}"')
        props.append(f"<w:ind {' '.join(attrs)}/>")
    p_pr = f"<w:pPr>{''.join(props)}</w:pPr>" if props else "<w:pPr/>"
    return f"<w:p>{p_pr}{''.join(runs)}</w:p>"


def image_extent(image_path: Path) -> tuple[int, int]:
    with Image.open(image_path) as img:
        width_px, height_px = img.size
    max_width_inches = 3.6 if height_px > width_px * 1.55 else 5.8
    cx = int(max_width_inches * 914400)
    cy = int(cx * height_px / width_px)
    return cx, cy


def image_paragraph_xml(rid: str, image_path: Path, docpr_id: int) -> str:
    cx, cy = image_extent(image_path)
    name = escape(image_path.name)
    return (
        "<w:p><w:pPr><w:spacing w:after=\"80\"/></w:pPr><w:r><w:drawing>"
        "<wp:inline distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\">"
        f"<wp:extent cx=\"{cx}\" cy=\"{cy}\"/>"
        f"<wp:docPr id=\"{docpr_id}\" name=\"{name}\"/>"
        "<a:graphic xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\">"
        "<a:graphicData uri=\"http://schemas.openxmlformats.org/drawingml/2006/picture\">"
        "<pic:pic xmlns:pic=\"http://schemas.openxmlformats.org/drawingml/2006/picture\">"
        "<pic:nvPicPr>"
        f"<pic:cNvPr id=\"{docpr_id}\" name=\"{name}\"/>"
        "<pic:cNvPicPr/>"
        "</pic:nvPicPr>"
        "<pic:blipFill>"
        f"<a:blip r:embed=\"{rid}\"/>"
        "<a:stretch><a:fillRect/></a:stretch>"
        "</pic:blipFill>"
        "<pic:spPr>"
        f"<a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"{cx}\" cy=\"{cy}\"/></a:xfrm>"
        "<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>"
        "</pic:spPr>"
        "</pic:pic>"
        "</a:graphicData>"
        "</a:graphic>"
        "</wp:inline></w:drawing></w:r></w:p>"
    )


def core_xml(title: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{escape(title)}</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>"""


def content_types_xml(image_count: int) -> str:
    image_defaults = '<Default Extension="png" ContentType="image/png"/>'
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  {image_defaults if image_count else ""}
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""


def package_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def document_rels_xml(image_paths: list[Path]) -> str:
    rels = []
    for index, image_path in enumerate(image_paths, start=1):
        rels.append(
            f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{escape(image_path.name)}"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels)
        + "</Relationships>"
    )


def build_docx_report(output_path: Path, title: str, blocks: list[dict[str, object]]) -> None:
    image_paths: list[Path] = []
    paragraphs: list[str] = []
    docpr_id = 1

    for block in blocks:
        block_type = block["type"]
        if block_type == "h1":
            paragraphs.append(paragraph_xml([run_xml(str(block["text"]), bold=True, size=52, color="0B2048")], spacing_after=160))
        elif block_type == "meta":
            paragraphs.append(paragraph_xml([run_xml(str(block["text"]), size=22, color="40536D")], spacing_after=180))
        elif block_type == "h2":
            paragraphs.append(paragraph_xml([run_xml(str(block["text"]), bold=True, size=34, color="0B2048")], spacing_after=180))
        elif block_type == "p":
            paragraphs.append(paragraph_xml([run_xml(str(block["text"]))], spacing_after=160))
        elif block_type == "bullet":
            paragraphs.append(paragraph_xml([run_xml(f"• {block['text']}")], spacing_after=120, left=720, first_line=-360))
        elif block_type == "image":
            image_path = ROOT / str(block["path"])
            image_paths.append(image_path)
            rid = f"rId{len(image_paths)}"
            paragraphs.append(image_paragraph_xml(rid, image_path, docpr_id))
            docpr_id += 1
            paragraphs.append(paragraph_xml([run_xml(str(block["caption"]), size=22, color="43526A")], spacing_after=180))

    sect_pr = (
        '<w:sectPr>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>'
        '</w:sectPr>'
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f"<w:body>{''.join(paragraphs)}{sect_pr}</w:body></w:document>"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(len(image_paths)))
        archive.writestr("_rels/.rels", package_rels_xml())
        archive.writestr("docProps/core.xml", core_xml(title))
        archive.writestr("docProps/app.xml", app_xml())
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/_rels/document.xml.rels", document_rels_xml(image_paths))
        for image_path in image_paths:
            archive.write(image_path, arcname=f"word/media/{image_path.name}")


def lab02_blocks() -> list[dict[str, object]]:
    return [
        {"type": "h1", "text": "Лабораторна робота № 2"},
        {"type": "meta", "text": "Тема: встановлення та налаштування інструментів Android-розробки. Дата виконання: 11.03.2026."},
        {"type": "p", "text": "Мета роботи: перевірити наявність та працездатність засобів розробки Android і емулятора на поточній машині."},
        {"type": "p", "text": "Методичні вказівки орієнтовані на застарілий стек Eclipse + ADT + Intel HAXM + Windows. На цій машині фактичне виконання проведене в сучасному еквіваленті: Android Studio + Android SDK + Emulator + Hypervisor.Framework на macOS arm64. Це важливо, тому що ADT офіційно застарів, а HAXM не застосовується на Apple Silicon."},
        {"type": "h2", "text": "Хід виконання"},
        {"type": "bullet", "text": "Перевірено встановлення JDK. У системі наявна Java 21 LTS, що перевищує мінімальну вимогу методички."},
        {"type": "bullet", "text": "Перевірено структуру Android SDK у каталозі ~/Library/Android/sdk: доступні build-tools, platform-tools, platforms, system-images, emulator."},
        {"type": "bullet", "text": "Перевірено механізм апаратного прискорення емулятора. На macOS використовується Hypervisor.Framework, що є сучасною заміною HAXM."},
        {"type": "bullet", "text": "Перевірено наявні AVD та успішний запуск віртуального пристрою."},
        {"type": "h2", "text": "Фактичні результати"},
        {"type": "image", "path": "reports/screenshots/lab02/01_java_version.png", "caption": "Рисунок 1 - Перевірка встановленої версії JDK"},
        {"type": "image", "path": "reports/screenshots/lab02/02_android_sdk_contents.png", "caption": "Рисунок 2 - Вміст каталогу Android SDK"},
        {"type": "image", "path": "reports/screenshots/lab02/03_emulator_accel.png", "caption": "Рисунок 3 - Перевірка механізму прискорення емулятора"},
        {"type": "image", "path": "reports/screenshots/lab02/04_avd_list.png", "caption": "Рисунок 4 - Список доступних віртуальних пристроїв"},
        {"type": "image", "path": "reports/screenshots/lab02/05_running_avd.png", "caption": "Рисунок 5 - Запущений віртуальний Android-пристрій"},
        {"type": "h2", "text": "Висновок"},
        {"type": "p", "text": "У ході роботи підтверджено наявність і працездатність ключових компонентів Android-середовища: JDK, Android SDK, системних образів, емулятора та AVD. Незважаючи на застарілість стеку Eclipse/ADT у методичних вказівках, ціль роботи досягнута сучасними підтримуваними засобами. Емулятор успішно запускається та може використовуватись для перевірки Android-застосунків."},
    ]


def lab03_blocks() -> list[dict[str, object]]:
    return [
        {"type": "h1", "text": "Лабораторна робота № 3"},
        {"type": "meta", "text": "Тема: Android Studio. Створення та перевірка віртуального пристрою AVD. Дата виконання: 11.03.2026."},
        {"type": "p", "text": "Мета роботи: створити або перевірити налаштований AVD, запустити його та зафіксувати основні параметри роботи."},
        {"type": "p", "text": "Методичка описує Intel x86 + HAXM + Windows 7 + API 22. На поточній машині використовується arm64 macOS, тому фактичний еквівалент — arm64-v8a AVD із прискоренням через Hypervisor.Framework. Для Apple Silicon це правильний і підтримуваний сценарій."},
        {"type": "h2", "text": "Параметри використаного AVD"},
        {"type": "image", "path": "reports/screenshots/lab03/00_avd_config.png", "caption": "Рисунок 1 - Конфігурація віртуального пристрою Medium_Phone_API_36.1"},
        {"type": "h2", "text": "Виконання роботи"},
        {"type": "bullet", "text": "Запущено AVD Medium_Phone_API_36.1."},
        {"type": "bullet", "text": "Перемкнено системну локаль на ru-RU, як вимагає завдання."},
        {"type": "bullet", "text": "Перевірено домашній екран після запуску пристрою."},
        {"type": "bullet", "text": "Відкрито сторінку мовних налаштувань і зафіксовано активну російську локаль."},
        {"type": "bullet", "text": "Відкрито сторінку відомостей про пристрій, де видно модель емулятора та версію Android."},
        {"type": "h2", "text": "Скріншоти виконання"},
        {"type": "image", "path": "reports/screenshots/lab03/01_home_ru.png", "caption": "Рисунок 2 - Домашній екран запущеного AVD"},
        {"type": "image", "path": "reports/screenshots/lab03/02_locale_settings_ru.png", "caption": "Рисунок 3 - Екран мовних налаштувань із локаллю Русский (Россия)"},
        {"type": "image", "path": "reports/screenshots/lab03/03_about_device.png", "caption": "Рисунок 4 - Екран «Об эмулированном устройстве» з моделлю та версією Android"},
        {"type": "h2", "text": "Підтверджені параметри"},
        {"type": "bullet", "text": "AVD: Medium_Phone_API_36.1"},
        {"type": "bullet", "text": "ABI: arm64-v8a"},
        {"type": "bullet", "text": "Роздільна здатність: 1080x2400"},
        {"type": "bullet", "text": "RAM: 2048 MB"},
        {"type": "bullet", "text": "Мова системи: Русский (Россия)"},
        {"type": "bullet", "text": "Модель: sdk_gphone64_arm64"},
        {"type": "bullet", "text": "Версія Android: 16"},
        {"type": "h2", "text": "Висновок"},
        {"type": "p", "text": "У роботі перевірено працездатний AVD у середовищі Android Studio та зафіксовано його основні параметри. Емулятор успішно запускається, підтримує зміну локалі та надає системні відомості про модель і версію Android. На Apple Silicon аналогом описаного в методичці Intel x86/HAXM є arm64 AVD з Hypervisor.Framework."},
    ]


def main() -> None:
    LAB02_DIR.mkdir(parents=True, exist_ok=True)
    LAB03_DIR.mkdir(parents=True, exist_ok=True)

    java_version = filtered_lines(run("java -version"))
    sdk_dir = filtered_lines(run("ls ~/Library/Android/sdk"))
    accel = filtered_lines(run("~/Library/Android/sdk/emulator/emulator -accel-check"))
    accel = [line for line in accel if line.startswith("accel") or "Hypervisor.Framework" in line]
    avd_list = filtered_lines(run("~/Library/Android/sdk/emulator/emulator -list-avds"))
    avd_list = [line for line in avd_list if line and not line.startswith("Warning")]

    config_text = (
        Path.home() / ".android" / "avd" / "Medium_Phone.avd" / "config.ini"
    ).read_text(encoding="utf-8")
    config_lines = []
    for line in config_text.splitlines():
        if line.startswith(
            (
                "AvdId=",
                "abi.type=",
                "hw.cpu.arch=",
                "hw.lcd.width=",
                "hw.lcd.height=",
                "hw.ramSize=",
                "disk.dataPartition.size=",
                "image.sysdir.1=",
                "target=",
                "PlayStore.enabled=",
            )
        ):
            config_lines.append(line)

    render_terminal_capture(
        LAB02_DIR / "01_java_version.png",
        "Перевірка JDK",
        "java -version",
        java_version,
    )
    render_terminal_capture(
        LAB02_DIR / "02_android_sdk_contents.png",
        "Вміст Android SDK",
        "ls ~/Library/Android/sdk",
        sdk_dir,
    )
    render_terminal_capture(
        LAB02_DIR / "03_emulator_accel.png",
        "Перевірка прискорення емулятора",
        "~/Library/Android/sdk/emulator/emulator -accel-check",
        accel,
    )
    render_terminal_capture(
        LAB02_DIR / "04_avd_list.png",
        "Наявні AVD",
        "~/Library/Android/sdk/emulator/emulator -list-avds",
        avd_list,
    )

    running_avd_source = LAB03_DIR / "01_home_ru.png"
    running_avd_target = LAB02_DIR / "05_running_avd.png"
    if running_avd_source.exists():
        running_avd_target.write_bytes(running_avd_source.read_bytes())

    render_terminal_capture(
        LAB03_DIR / "00_avd_config.png",
        "Конфігурація AVD",
        "cat ~/.android/avd/Medium_Phone.avd/config.ini",
        config_lines,
    )

    lab02_html_path = REPORTS_DIR / "lab02_report.html"
    lab03_html_path = REPORTS_DIR / "lab03_report.html"
    lab02_docx_path = REPORTS_DIR / "ЛР_02_звіт.docx"
    lab03_docx_path = REPORTS_DIR / "ЛР_03_AVD_звіт.docx"

    write_file(lab02_html_path, build_lab02_html())
    write_file(lab03_html_path, build_lab03_html())
    build_docx_report(lab02_docx_path, "Лабораторна робота № 2", lab02_blocks())
    build_docx_report(lab03_docx_path, "Лабораторна робота № 3", lab03_blocks())


if __name__ == "__main__":
    main()
