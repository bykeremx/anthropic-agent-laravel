# -*- coding: utf-8 -*-
"""AI mimarisi teknik dokümantasyon PDF üreticisi (reportlab)."""
import math
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Flowable, Frame, KeepTogether, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle, XPreformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents

PROJECT = r"C:\Users\mkere\Desktop\Herd\exampleai"
OUT = sys.argv[1] if len(sys.argv) > 1 else "AI_Mimari_Dokumantasyonu.pdf"

# ---------------------------------------------------------------- fonts
F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Sans", os.path.join(F, "arial.ttf")))
pdfmetrics.registerFont(TTFont("Sans-B", os.path.join(F, "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Sans-I", os.path.join(F, "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Sans-BI", os.path.join(F, "arialbi.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(F, "consola.ttf")))
pdfmetrics.registerFont(TTFont("Mono-B", os.path.join(F, "consolab.ttf")))
pdfmetrics.registerFont(TTFont("Mono-I", os.path.join(F, "consolai.ttf")))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-BI")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-B", italic="Mono-I", boldItalic="Mono-B")

# ---------------------------------------------------------------- colors
NAVY = colors.HexColor("#1F3A5F")
TEAL = colors.HexColor("#2E7D9A")
INK = colors.HexColor("#1E2329")
MUTED = colors.HexColor("#5B6673")
RULE = colors.HexColor("#D8DEE6")
CODE_BG = colors.HexColor("#F6F8FA")
NOTE_BG = colors.HexColor("#EEF5F8")
WARN_BG = colors.HexColor("#FFF6E5")
WARN_BD = colors.HexColor("#E0A526")

# ---------------------------------------------------------------- styles
ST = {
    "body": ParagraphStyle("body", fontName="Sans", fontSize=9.6, leading=14, textColor=INK, spaceAfter=5),
    "small": ParagraphStyle("small", fontName="Sans", fontSize=8.2, leading=11, textColor=MUTED),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=8.3, leading=11, textColor=INK),
    "cellh": ParagraphStyle("cellh", fontName="Sans-B", fontSize=8.3, leading=11, textColor=colors.white),
    "bullet": ParagraphStyle("bullet", fontName="Sans", fontSize=9.6, leading=13.6, textColor=INK,
                             leftIndent=14, bulletIndent=3, spaceAfter=2.5),
    "H1": ParagraphStyle("H1", fontName="Sans-B", fontSize=19, leading=24, textColor=NAVY,
                         spaceBefore=4, spaceAfter=10),
    "H2": ParagraphStyle("H2", fontName="Sans-B", fontSize=13.2, leading=17, textColor=NAVY,
                         spaceBefore=12, spaceAfter=6),
    "H3": ParagraphStyle("H3", fontName="Sans-B", fontSize=10.6, leading=14, textColor=TEAL,
                         spaceBefore=9, spaceAfter=4),
    "H4": ParagraphStyle("H4", fontName="Sans-B", fontSize=9.6, leading=13, textColor=INK,
                         spaceBefore=6, spaceAfter=2),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=7.5, leading=9.5, textColor=INK),
    "snipref": ParagraphStyle("snipref", fontName="Mono", fontSize=7.4, leading=9, textColor=MUTED,
                              spaceBefore=7, spaceAfter=1),
}

MONO_INLINE = '<font face="Mono" size="8.8" color="#8A1F3D">'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(s):
    """Basit işaretleme: `kod`, **kalın**, *italik*."""
    s = esc(s)
    s = re.sub(r"`([^`]+)`", lambda m: MONO_INLINE + m.group(1) + "</font>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", s)
    return s


story = []


def P(text, style="body"):
    story.append(Paragraph(fmt(text), ST[style]))


def H1(text, brk=True):
    story.append(PageBreak() if brk else CondPageBreak(260))
    story.append(Paragraph(esc(text), ST["H1"]))
    story.append(HRule())


def H2(text):
    story.append(CondPageBreak(60 * mm * 0.5))
    story.append(Paragraph(esc(text), ST["H2"]))


def H3(text):
    story.append(CondPageBreak(30))
    story.append(Paragraph(esc(text), ST["H3"]))


def H4(text):
    story.append(Paragraph(esc(text), ST["H4"]))


def BL(items):
    for it in items:
        story.append(Paragraph(fmt(it), ST["bullet"], bulletText="•"))


def NL(items):
    for i, it in enumerate(items, 1):
        story.append(Paragraph(fmt(it), ST["bullet"], bulletText=f"{i}."))


def SP(h=6):
    story.append(Spacer(1, h))


class HRule(Flowable):
    def wrap(self, aw, ah):
        self.aw = aw
        return aw, 8

    def draw(self):
        self.canv.setStrokeColor(TEAL)
        self.canv.setLineWidth(1.4)
        self.canv.line(0, 6, 60, 6)
        self.canv.setStrokeColor(RULE)
        self.canv.setLineWidth(0.6)
        self.canv.line(60, 6, self.aw, 6)


def callout(text, kind="note", title=None):
    bg, bd = (NOTE_BG, TEAL) if kind == "note" else (WARN_BG, WARN_BD)
    body = (f"<b>{esc(title)}</b><br/>" if title else "") + fmt(text)
    t = Table([[Paragraph(body, ST["cell"])]], colWidths=["100%"])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, bd),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(Spacer(1, 3))
    story.append(t)
    story.append(Spacer(1, 6))


def table(rows, widths, header=True, mono_first=False):
    data = []
    for r, row in enumerate(rows):
        cells = []
        for c, val in enumerate(row):
            if header and r == 0:
                cells.append(Paragraph(esc(val), ST["cellh"]))
            elif mono_first and c == 0:
                cells.append(Paragraph(f'<font face="Mono" size="7.8">{esc(val)}</font>', ST["cell"]))
            else:
                cells.append(Paragraph(fmt(val), ST["cell"]))
        data.append(cells)
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
        for i in range(1, len(rows)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FB")))
    t.setStyle(TableStyle(style))
    story.append(Spacer(1, 2))
    story.append(t)
    story.append(Spacer(1, 8))


# ---------------------------------------------------------------- code blocks
WRAP = 104


def read_src(rel):
    with open(os.path.join(PROJECT, rel), encoding="utf-8") as fh:
        return fh.read().replace("\r\n", "\n").rstrip("\n")


def color_line(line):
    """Yorumları renklendir (satır başı veya kod sonrası //)."""
    stripped = line.lstrip()
    if stripped.startswith(("//", "/*", "*", "#")):
        return f'<font color="#6A8A5A">{esc(line)}</font>'
    idx = None
    in_s, q = False, ""
    for i, ch in enumerate(line):
        if in_s:
            if ch == q and line[i - 1] != "\\":
                in_s = False
        elif ch in "'\"":
            in_s, q = True, ch
        elif line.startswith("//", i):
            idx = i
            break
    if idx is not None:
        return esc(line[:idx]) + f'<font color="#6A8A5A">{esc(line[idx:])}</font>'
    return esc(line)


def code_xml(text, start=1, numbered=True):
    out = []
    for n, line in enumerate(text.split("\n"), start):
        chunks = [line[i:i + WRAP] for i in range(0, max(len(line), 1), WRAP)] or [""]
        for k, ch in enumerate(chunks):
            if numbered:
                num = f"{n:>3}" if k == 0 else "  »"
                out.append(f'<font color="#9AA5B1">{num}</font>  ' + color_line(ch))
            else:
                out.append(color_line(ch) if k == 0 else "  " + color_line(ch))
    return "\n".join(out)


def code_style(bg=CODE_BG):
    return ParagraphStyle("cb", parent=ST["code"], backColor=bg, borderColor=RULE, borderWidth=0.5,
                          borderPadding=(5, 6, 5, 6), spaceBefore=4, spaceAfter=9)


def code(text, numbered=False, start=1):
    block = XPreformatted(code_xml(text, start, numbered), code_style())
    story.append(KeepTogether([block]) if text.count("\n") < 45 else block)


def file_bar(path, extra=""):
    t = Table([[Paragraph(f'<font face="Mono-B" size="8.5" color="#FFFFFF">{esc(path)}</font>'
                          + (f'<font size="7.5" color="#B9C6D6">   {esc(extra)}</font>' if extra else ""),
                          ST["cell"])]], colWidths=["100%"])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def full_source(rel):
    src = read_src(rel)
    n = src.count("\n") + 1
    story.append(CondPageBreak(80))
    story.append(file_bar(rel, f"{n} satır · eksiksiz"))
    story.append(Spacer(1, 2))
    story.append(XPreformatted(code_xml(src, 1, True), code_style()))


def snip(rel, a, b, notes):
    """Gerçek dosyadan a..b satırlarını göster, ardından açıklamaları ekle."""
    lines = read_src(rel).split("\n")[a - 1:b]
    label = f"{rel} · satır {a}" + (f"–{b}" if b != a else "")
    block = [Paragraph(esc(label), ST["snipref"]),
             XPreformatted(code_xml("\n".join(lines), a, True), code_style())]
    story.append(KeepTogether(block))
    for n_ in notes if isinstance(notes, list) else [notes]:
        P(n_)


# ---------------------------------------------------------------- diagrams
KIND = {
    "ui":   (colors.HexColor("#E3ECF7"), colors.HexColor("#3D6EA8")),
    "http": (colors.HexColor("#E8EEF5"), colors.HexColor("#1F3A5F")),
    "ai":   (colors.HexColor("#DFF1F4"), colors.HexColor("#2E7D9A")),
    "tool": (colors.HexColor("#FDF1DC"), colors.HexColor("#C98A12")),
    "ext":  (colors.HexColor("#EDE6F7"), colors.HexColor("#6B4BA8")),
    "err":  (colors.HexColor("#FBE6E6"), colors.HexColor("#B3403A")),
    "cfg":  (colors.HexColor("#EFF1F3"), colors.HexColor("#6B7682")),
    "data": (colors.HexColor("#E6F3E8"), colors.HexColor("#3E8A4F")),
}


class Diagram(Flowable):
    def __init__(self, w, h, painter, scale=1.0):
        super().__init__()
        self.w, self.h, self.painter, self.scale = w, h, painter, scale

    def wrap(self, aw, ah):
        return self.w * self.scale, self.h * self.scale

    def draw(self):
        c = self.canv
        c.saveState()
        c.scale(self.scale, self.scale)
        self.painter(DrawKit(c, self.h))
        c.restoreState()


class DrawKit:
    def __init__(self, c, H):
        self.c, self.H = c, H

    def y(self, t):
        return self.H - t

    def _fit(self, text, font, size, maxw):
        while size > 5 and pdfmetrics.stringWidth(text, font, size) > maxw:
            size -= 0.25
        return size

    def box(self, x, t, w, h, lines, kind="ai", dashed=False):
        c = self.c
        fill, stroke = KIND[kind]
        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        c.setLineWidth(1)
        if dashed:
            c.setDash(3, 2)
        c.roundRect(x, self.y(t + h), w, h, 5, fill=1, stroke=1)
        c.setDash()
        self._text_block(x + w / 2, t + h / 2, w - 10, lines, stroke)

    def _text_block(self, cx, tc, maxw, lines, head_color):
        c = self.c
        sizes = [8.2] + [7.0] * (len(lines) - 1)
        lead = [s + 2.4 for s in sizes]
        total = sum(lead) - 2.4
        cur = tc - total / 2
        for i, line in enumerate(lines):
            font = "Sans-B" if i == 0 else "Sans"
            size = self._fit(line, font, sizes[i], maxw)
            c.setFillColor(head_color if i == 0 else INK)
            c.setFont(font, size)
            c.drawCentredString(cx, self.y(cur + sizes[i] * 0.8), line)
            cur += lead[i]

    def diamond(self, cx, tc, hw, hh, lines, kind="ai"):
        c = self.c
        fill, stroke = KIND[kind]
        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        p = c.beginPath()
        p.moveTo(cx, self.y(tc - hh))
        p.lineTo(cx + hw, self.y(tc))
        p.lineTo(cx, self.y(tc + hh))
        p.lineTo(cx - hw, self.y(tc))
        p.close()
        c.drawPath(p, fill=1, stroke=1)
        self._text_block(cx, tc, hw * 1.15, lines, stroke)

    def arrow(self, pts, color=MUTED, dashed=False, width=1.0):
        c = self.c
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(width)
        if dashed:
            c.setDash(3, 2)
        p = c.beginPath()
        p.moveTo(pts[0][0], self.y(pts[0][1]))
        for x, t in pts[1:]:
            p.lineTo(x, self.y(t))
        c.drawPath(p, stroke=1, fill=0)
        c.setDash()
        (x1, t1), (x2, t2) = pts[-2], pts[-1]
        ang = math.atan2(self.y(t2) - self.y(t1), x2 - x1)
        L, Wd = 6.5, 3.2
        bx, by = x2 - L * math.cos(ang), self.y(t2) - L * math.sin(ang)
        p = c.beginPath()
        p.moveTo(x2, self.y(t2))
        p.lineTo(bx + Wd * math.sin(ang), by - Wd * math.cos(ang))
        p.lineTo(bx - Wd * math.sin(ang), by + Wd * math.cos(ang))
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def label(self, x, t, text, size=6.8, color=MUTED, align="left", bold=False):
        c = self.c
        c.setFillColor(color)
        c.setFont("Sans-B" if bold else "Sans-I", size)
        if align == "center":
            c.drawCentredString(x, self.y(t), text)
        elif align == "right":
            c.drawRightString(x, self.y(t), text)
        else:
            c.drawString(x, self.y(t), text)


def paint_flow(k):
    MX, MW = 72, 228          # ana kolon
    MC = MX + MW / 2          # 186
    RX, RW = 322, 161         # sağ kolon
    RC = RX + RW / 2
    RED = KIND["err"][1]

    main = [
        (0, 40, ["1  Tarayıcı · x-ai.chat bileşeni", "fetch POST {message}",
                 "Accept: application/json · X-CSRF-TOKEN"], "ui"),
        (56, 36, ["2  routes/web.php", "POST /ai/agent/send  →  route adı: ai.send"], "http"),
        (108, 36, ["3  web middleware grubu", "oturum (session) · CSRF token doğrulaması"], "http"),
        (160, 36, ["4  AgentController::post()", "validate: message → required|string|max:2000"], "http"),
        (212, 48, ["5  Service Container (method injection)", "new AiAgent(new AiClient, new ToolsService)",
                   "__construct: $tools = ToolSchema::all()"], "ai"),
        (276, 36, ["6  AiAgent::run($messages)", "for ($step = 0; $step < maxSteps(5); $step++)"], "ai"),
        (328, 40, ["7  AiClient::send(messages, system, tools)",
                   "payload: model · max_tokens 1024 · system · tools"], "ai"),
        (384, 48, ["8  Anthropic Messages API (Claude)", "POST https://api.anthropic.com/v1/messages",
                   "Http::timeout(30) → throw() → json()"], "ext"),
    ]
    for i, (t, h, lines, kind) in enumerate(main):
        k.box(MX, t, MW, h, lines, kind)
        if i:
            pt, ph = main[i - 1][0], main[i - 1][1]
            k.arrow([(MC, pt + ph), (MC, t)])

    # karar
    k.arrow([(MC, 432), (MC, 444)])
    k.diamond(MC, 472, 82, 28, ["stop_reason", "== 'tool_use' ?"], "ai")

    tail = [
        (516, 36, ["13  return $response", "end_turn · max_tokens · max_steps …"], "ai"),
        (568, 40, ["14  AiAgent::text($response)", "type = text blokları \"\\n\" ile birleştirilir"], "ai"),
        (624, 48, ["15  response()->json(['reply' => …])", "HTTP 200 · chat bileşeni cevabı",
                   "asistan balonu olarak çizer"], "ui"),
    ]
    k.arrow([(MC, 500), (MC, 516)])
    k.label(MC + 6, 511, "Hayır", bold=True, color=KIND["ai"][1])
    for i, (t, h, lines, kind) in enumerate(tail):
        k.box(MX, t, MW, h, lines, kind)
        if i:
            pt, ph = tail[i - 1][0], tail[i - 1][1]
            k.arrow([(MC, pt + ph), (MC, t)])

    # sağ kolon: yan kutular
    side = [
        (108, 36, ["CSRF token geçersiz", "→ 419 Page Expired"], "err", "out"),
        (160, 36, ["Doğrulama hatası (ValidationException)", "→ 422 JSON {message, errors}"], "err", "out"),
        (212, 48, ["app/Schema/ToolSchema.php", "all(): tool tanımları (ad · açıklama · şema)",
                   "get_customer_orders · get_order_status"], "cfg", "in"),
        (276, 36, ["5 tur dolarsa: sentetik yanıt", "stop_reason = max_steps → 14'e gider"], "cfg", "out"),
        (328, 40, ["config/services.php ← .env", "ANTHROPIC_API_KEY · ANTHROPIC_MODEL"], "cfg", "in"),
        (384, 48, ["4xx/5xx → RequestException → log → 502", "timeout / bağlantı / diğer hata",
                   "→ Throwable → log → 500"], "err", "out"),
    ]
    for t, h, lines, kind, d in side:
        k.box(RX, t, RW, h, lines, kind)
        mid = t + h / 2
        col = RED if kind == "err" else MUTED
        if d == "out":
            k.arrow([(MX + MW, mid), (RX, mid)], color=col, dashed=kind != "err")
        else:
            k.arrow([(RX, mid), (MX + MW, mid)], color=col, dashed=True)

    # tool kolonu
    tools = [
        (448, 48, ["9  ToolsService::call(name, input)", "whitelist: ToolSchema'daki adlar",
                   "+ method_exists() kontrolü"], "tool"),
        (512, 44, ["10  get_customer_orders() | get_order_status()",
                   "girdi normalizasyonu · formatOrder()"], "tool"),
        (572, 40, ["11  Eloquent → Veritabanı", "Customer::with('orders') · Order::with('customer')"], "data"),
        (624, 48, ["12  tool_result blokları", "assistant mesajı + tek user mesajı",
                   "$messages dizisine eklenir"], "tool"),
    ]
    for i, (t, h, lines, kind) in enumerate(tools):
        k.box(RX, t, RW, h, lines, kind)
        if i:
            pt, ph = tools[i - 1][0], tools[i - 1][1]
            k.arrow([(RC, pt + ph), (RC, t)], color=KIND["tool"][1])
    k.arrow([(MC + 82, 472), (RX, 472)], color=KIND["tool"][1])
    k.label(MC + 92, 466, "Evet", bold=True, color=KIND["tool"][1])

    # döngü geri dönüşü
    LOOP = KIND["tool"][1]
    k.arrow([(RC, 672), (RC, 696), (22, 696), (22, 294), (MX, 294)], color=LOOP, width=1.2)
    k.label(MC, 710, "Döngü: $step + 1 → güncellenmiş $messages ile 6. adıma (tekrar AiClient::send) dön",
            align="center", color=LOOP, size=7)


def paint_deps(k):
    k.box(5, 0, 200, 40, ["chat.blade.php (x-ai.chat)", "resources/views/components/ai"], "ui")
    k.box(283, 0, 200, 40, ["routes/web.php", "ai.agent (GET) · ai.send (POST)"], "http")
    k.arrow([(205, 20), (283, 20)])
    k.label(244, 15, "HTTP POST", align="center")

    k.box(141, 80, 200, 42, ["AgentController", "index() · post()"], "http")
    k.arrow([(383, 40), (383, 60), (300, 60), (300, 80)])
    k.label(388, 70, "route → controller action")

    k.box(141, 168, 200, 44, ["AiAgent", "run() · text() · $system · $tools · $maxSteps"], "ai")
    k.arrow([(241, 122), (241, 168)])
    k.label(247, 140, "method injection: post(Request, AiAgent)")
    k.label(247, 150, "statik: AiAgent::text($response)")

    k.box(5, 268, 140, 44, ["AiClient", "send(messages, system, tools)"], "ai")
    k.box(171, 268, 140, 44, ["ToolsService", "call() · 2 tool · formatOrder()"], "tool")
    k.box(343, 268, 140, 44, ["ToolSchema", "static all(): array"], "cfg")
    k.arrow([(190, 212), (190, 240), (75, 240), (75, 268)])
    k.label(80, 236, "constructor injection")
    k.arrow([(241, 212), (241, 268)])
    k.label(246, 252, "constructor injection")
    k.arrow([(292, 212), (292, 240), (413, 240), (413, 268)], dashed=True)
    k.label(300, 236, "statik: ToolSchema::all()")
    k.arrow([(311, 290), (343, 290)], dashed=True)
    k.label(327, 285, "whitelist", align="center", size=6)

    k.box(5, 348, 140, 40, ["Http facade + config()", "services.anthropic.key / model"], "cfg")
    k.box(171, 348, 140, 40, ["Customer · Order", "Eloquent modelleri (hasMany/belongsTo)"], "data")
    k.arrow([(75, 312), (75, 348)])
    k.arrow([(241, 312), (241, 348)])

    k.box(5, 420, 140, 36, ["Anthropic Messages API", "api.anthropic.com/v1/messages"], "ext")
    k.box(171, 420, 140, 36, ["Veritabanı", "customers · orders tabloları"], "data")
    k.arrow([(75, 388), (75, 420)])
    k.arrow([(241, 388), (241, 420)])

    # lejant
    lx, lt = 343, 350
    items = [("ui", "Arayüz"), ("http", "HTTP / Laravel"), ("ai", "AI servis katmanı"),
             ("tool", "Tool yürütme"), ("data", "Veri"), ("cfg", "Şema / yapılandırma"),
             ("ext", "Dış servis"), ("err", "Hata çıkışı")]
    k.label(lx, lt - 6, "Renkler", bold=True, color=INK, size=7.5)
    for i, (kd, name) in enumerate(items):
        fill, stroke = KIND[kd]
        col, row = i % 2, i // 2
        x, t = lx + col * 72, lt + row * 14
        k.c.setFillColor(fill)
        k.c.setStrokeColor(stroke)
        k.c.rect(x, k.y(t + 8), 10, 8, fill=1, stroke=1)
        k.label(x + 14, t + 7, name, color=INK, size=6.6)


# ---------------------------------------------------------------- document
class Doc(BaseDocTemplate):
    def __init__(self, fn):
        super().__init__(fn, pagesize=A4, leftMargin=56, rightMargin=56, topMargin=58, bottomMargin=52,
                         title="AI Agent Mimarisi — Teknik Dokümantasyon", author="exampleai",
                         subject="Laravel + Anthropic tool-use agent mimarisi")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[frame], onPage=self._cover),
            PageTemplate(id="body", frames=[frame], onPage=self._page),
        ])
        self._seq = 0

    def _cover(self, c, d):
        c.saveState()
        c.setFillColor(NAVY)
        c.rect(0, A4[1] - 250, A4[0], 250, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(0, A4[1] - 256, A4[0], 6, fill=1, stroke=0)
        c.restoreState()

    def _page(self, c, d):
        c.saveState()
        c.setFont("Sans", 7.5)
        c.setFillColor(MUTED)
        c.drawString(56, A4[1] - 36, "exampleai · AI Agent Mimarisi — Teknik Dokümantasyon")
        c.drawRightString(A4[0] - 56, A4[1] - 36, "Laravel 13 · Anthropic Messages API")
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(56, A4[1] - 42, A4[0] - 56, A4[1] - 42)
        c.drawRightString(A4[0] - 56, 30, f"Sayfa {d.page}")
        c.restoreState()

    def beforeDocument(self):
        self._seq = 0

    def afterFlowable(self, fl):
        if isinstance(fl, Paragraph) and fl.style.name in ("H1", "H2"):
            level = 0 if fl.style.name == "H1" else 1
            text = fl.getPlainText()
            key = f"h{self._seq}"
            self._seq += 1
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
            self.notify("TOCEntry", (level, text, self.page, key))


# ================================================================= CONTENT
# ---------------------------------------------------------------- 1. Kapak
cover_t = ParagraphStyle("ct", fontName="Sans-B", fontSize=30, leading=36, textColor=colors.white)
cover_s = ParagraphStyle("cs", fontName="Sans", fontSize=13, leading=18, textColor=colors.HexColor("#CFE0EE"))
story.append(Spacer(1, 40))
story.append(Paragraph("AI Agent Mimarisi", cover_t))
story.append(Paragraph("Teknik Dokümantasyon", ParagraphStyle("ct2", parent=cover_t, fontSize=22, leading=30,
                                                              textColor=colors.HexColor("#9FD3E3"))))
story.append(Spacer(1, 10))
story.append(Paragraph("Laravel + Anthropic Claude ile tool-use tabanlı müşteri hizmetleri asistanı:"
                       " mimari, veri akışı, tasarım kararları ve kaynak kodun tamamı", cover_s))
story.append(Spacer(1, 110))
story.append(Table(
    [[Paragraph("<b>Proje</b>", ST["cell"]), Paragraph("exampleai (Laravel 13, PHP 8.3)", ST["cell"])],
     [Paragraph("<b>Kapsam</b>", ST["cell"]), Paragraph(
         '<font face="Mono" size="8">app/Http/Controllers/Ai/AgentController.php<br/>'
         'app/Services/Ai/AiAgent.php<br/>app/Services/Ai/AiClient.php<br/>'
         'app/Services/Ai/ToolsService.php<br/>app/Schema/ToolSchema.php</font>', ST["cell"])],
     [Paragraph("<b>Bağlam olarak incelenenler</b>", ST["cell"]), Paragraph(
         "routes/web.php, config/services.php, app/Models/Customer.php, app/Models/Order.php, "
         "customers/orders migration'ları, resources/views/ai/agent.blade.php, "
         "resources/views/components/ai/chat.blade.php", ST["cell"])],
     [Paragraph("<b>Hedef okuyucu</b>", ST["cell"]), Paragraph(
         "Projeye aylar sonra dönen veya projeye yeni katılan geliştirici", ST["cell"])],
     [Paragraph("<b>Tarih</b>", ST["cell"]), Paragraph("12 Ekim 2026", ST["cell"])]],
    colWidths=[130, 353],
    style=TableStyle([("LINEBELOW", (0, 0), (-1, -2), 0.5, RULE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                      ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)])))
story.append(Spacer(1, 24))
story.append(Paragraph(
    "Not: Bu dokümandaki tüm kod alıntıları ve tam kaynak kodları, PDF üretildiği anda doğrudan proje "
    "dosyalarından okunmuştur; satır numaraları gerçek dosyalarla birebir aynıdır.", ST["small"]))
story.append(NextPageTemplate("body"))
story.append(PageBreak())

# ---------------------------------------------------------------- 2. İçindekiler
story.append(Paragraph("İçindekiler", ST["H1"].clone("toc_h")))
story.append(HRule())
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle("t0", fontName="Sans-B", fontSize=10.5, leading=15, leftIndent=0, firstLineIndent=0,
                   spaceBefore=5, textColor=NAVY),
    ParagraphStyle("t1", fontName="Sans", fontSize=9, leading=12.5, leftIndent=16, firstLineIndent=0,
                   textColor=INK),
]
toc.dotsMinLevel = 0
story.append(toc)

# ================================================================ 1. GENEL MİMARİ
H1("1. Genel Mimari")
H2("1.1 Sistem ne yapıyor?")
P("Bu modül, bir e-ticaret mağazası için Türkçe konuşan bir **müşteri hizmetleri asistanıdır**. Kullanıcı "
  "tarayıcıdaki sohbet kutusuna doğal dilde bir soru yazar (ör. “ORD-1003 siparişinin durumu ne?” veya "
  "“Ayşe Demir toplam ne kadar harcamış?”). Soru Laravel üzerinden Anthropic'in Claude modeline iletilir.")
P("Model soruyu cevaplamak için veritabanına bakması gerektiğine karar verirse **kendisi SQL çalıştırmaz**. "
  "Bunun yerine, uygulamanın önceden tanımladığı iki **tool**'dan (araç) birini belirli parametrelerle çağırmak "
  "istediğini bildirir. Laravel bu isteği güvenli şekilde yerel bir PHP metoduna çevirir, Eloquent ile veriyi "
  "okur, sonucu modele geri yollar. Model de son cevabı bu gerçek veriye dayanarak üretir.")
P("Bu desene **tool use (function calling) ile çalışan ajan döngüsü** (agent loop) denir. İş bölümü "
  "şöyledir: *ne* yapılacağına model karar verir, *nasıl* ve *hangi sınırlar içinde* yapılacağını uygulama "
  "belirler. Böylece model veriye yalnızca uygulamanın açtığı dar kapılardan erişebilir.")
callout("Ajan = LLM + araçlar + döngü. Model bir “beyin” gibidir ama veritabanına dokunamaz. ToolsService "
        "onun “elleri”, ToolSchema ellerin yapabileceği işlerin “menüsü”, AiAgent koordinatör, AiClient ise "
        "dış dünyaya açılan “telefon hattı”dır. AgentController de bu düzeneği HTTP dünyasına bağlayan kapıdır.",
        title="Zihinsel model")

H2("1.2 Katmanlar ve sorumluluklar")
table([
    ["Katman", "Dosya(lar)", "Sorumluluk"],
    ["Arayüz (UI)", "resources/views/ai/agent.blade.php, components/ai/chat.blade.php",
     "Sohbet ekranı; `fetch` ile JSON POST atar, `reply` alanını ekrana basar. (Kapsam dışı ama akışın başlangıcı.)"],
    ["Yönlendirme", "routes/web.php",
     "`GET /ai/agent` → sayfa, `POST /ai/agent/send` → mesaj uç noktası."],
    ["HTTP / Controller", "app/Http/Controllers/Ai/AgentController.php",
     "Girdiyi doğrular, ajanı çalıştırır, hataları HTTP durum kodlarına çevirir, JSON döner."],
    ["Orkestrasyon (Ajan)", "app/Services/Ai/AiAgent.php",
     "System prompt, tool listesi, çok adımlı döngü, tool sonuçlarını modele geri besleme, adım sınırı."],
    ["API istemcisi", "app/Services/Ai/AiClient.php",
     "Anthropic Messages API'ye tek bir HTTP çağrısı (URL, header, model, timeout)."],
    ["Tool yürütme", "app/Services/Ai/ToolsService.php",
     "Tool adını güvenle PHP metoduna eşler, Eloquent sorgularını çalıştırır, sonucu formatlar."],
    ["Sözleşme (Schema)", "app/Schema/ToolSchema.php",
     "Modele gösterilen tool tanımları: ad, açıklama, JSON Schema. Aynı zamanda whitelist kaynağı."],
    ["Veri", "app/Models/Customer.php, Order.php",
     "Eloquent modelleri; `Customer hasMany Order`, `Order belongsTo Customer`."],
    ["Yapılandırma", "config/services.php, .env",
     "`services.anthropic.key` ve `services.anthropic.model` değerleri."],
], [92, 150, 241])

H2("1.3 Temel tasarım kararları")
BL([
    "**Sorumlulukların ayrılması (Separation of Concerns).** HTTP işleri (Controller), iş akışı (AiAgent), dış "
    "servis iletişimi (AiClient), iş verisi (ToolsService) ve sözleşme (ToolSchema) ayrı dosyalardadır. Her biri "
    "diğerlerini bozmadan değiştirilebilir ve ayrı ayrı test edilebilir.",
    "**SDK yerine ham HTTP.** Resmî Anthropic SDK yerine Laravel'in `Http` facade'ı kullanılmıştır. Ek paket "
    "bağımlılığı yoktur, `Http::fake()` ile test edilebilir; timeout, retry, log gibi özellikler hazırdır.",
    "**Anthropic formatı sistemin ortak dilidir.** Katmanlar arasında özel DTO sınıfları yoktur; veri, Messages "
    "API'nin kendi JSON yapısıyla (PHP dizileri) taşınır: `$messages`, `content` blokları, `stop_reason`. "
    "Dönüştürme kodu gerekmez. Bedeli: tip güvenliği düşüktür, dizi anahtarlarını bilmek gerekir.",
    "**Tool tanımı ile tool uygulaması ayrıdır.** Modelin gördüğü tanım `ToolSchema`'da, çalışan kod "
    "`ToolsService`'tedir. İkisi tool adı üzerinden eşleşir: **tool adı = metod adı**.",
    "**Whitelist ile güvenli dinamik çağrı.** Model yalnızca `ToolSchema`'da listelenen adları çağırabilir; başka "
    "bir public metodu (ör. `call` veya `formatOrder`) tetikleyemez.",
    "**Sınırlı döngü.** `maxSteps = 5`; model sonsuz tool çağrısı zincirine giremez. Maliyet ve süre sınırlıdır.",
    "**Durumsuz (stateless) sohbet.** Her HTTP isteği yalnızca son kullanıcı mesajıyla başlar; önceki mesajlar "
    "sunucuya gönderilmez, saklanmaz (chat bileşenindeki yorum: “geçmiş tutulmaz”). Basitlik kazanılır; ancak "
    "“peki onun diğer siparişi?” gibi bağlama dayalı takip soruları çalışmaz.",
    "**Tool hataları exception değil, veridir.** Tool'lar `['status' => 'error', 'message' => …]` döner. Bu "
    "sonuç modele `is_error: true` ile iletilir ve model kullanıcıya doğal bir dille “bulunamadı” der. Sadece "
    "altyapı hataları (API, ağ) exception olarak yukarı çıkar.",
])

H2("1.4 Bileşenler nasıl haberleşiyor?")
table([
    ["Kaynak → Hedef", "Mekanizma", "Taşınan veri"],
    ["chat.blade → AgentController", "HTTP POST (JSON) + CSRF header", "`{message: string}`"],
    ["Laravel → AgentController::post", "Route + method injection", "`Request`, `AiAgent` örneği"],
    ["AgentController → AiAgent", "`run(array $messages)`", "`[['role' => 'user', 'content' => mesaj]]`"],
    ["AiAgent → AiClient", "Constructor injection, `send()`", "messages, system prompt, tools"],
    ["AiClient → Anthropic API", "HTTPS POST", "JSON payload → JSON yanıt (dizi)"],
    ["AiAgent → ToolSchema", "Statik `ToolSchema::all()`", "Tool tanımları dizisi"],
    ["AiAgent → ToolsService", "Constructor injection, `call(name, input)`", "Tool adı + girdi → sonuç dizisi"],
    ["ToolsService → ToolSchema", "Statik `ToolSchema::all()`", "Whitelist için tool adları"],
    ["ToolsService → Customer/Order", "Eloquent sorguları", "Model koleksiyonları"],
    ["AgentController → AiAgent::text", "Statik yardımcı", "Son yanıt → düz metin"],
    ["AgentController → chat.blade", "JSON yanıt", "`{reply}` (200) veya `{message}` (422/502/500)"],
], [150, 150, 183])
P("Dikkat edilirse **hiçbir sınıf bir diğerini `new` ile oluşturmaz**. Nesne grafiği (AiAgent → AiClient + "
  "ToolsService) tamamen Laravel Service Container tarafından kurulur. Statik çağrılar yalnızca durum taşımayan, "
  "saf veri/fonksiyon niteliğindeki yerlerde kullanılmıştır (`ToolSchema::all()`, `AiAgent::text()`).")

H2("1.5 Anthropic tool-use protokolü (kısa özet)")
P("Mimarinin neden bu şekilde kurulduğunu anlamak için API'nin tool-use sözleşmesini bilmek gerekir:")
NL([
    "İstemci `messages`, `system` ve `tools` (her biri ad + açıklama + `input_schema`) ile istek atar.",
    "Model bir tool kullanmak isterse yanıtın `stop_reason` değeri `tool_use` olur ve `content` dizisinde bir "
    "veya birden fazla `{type: 'tool_use', id, name, input}` bloğu bulunur.",
    "İstemci bu tool'ları kendisi çalıştırır. Modelin yanıtını **olduğu gibi** `assistant` mesajı olarak "
    "geçmişe ekler, ardından **tek bir** `user` mesajı içinde her tool için `{type: 'tool_result', tool_use_id, "
    "content, is_error}` bloğu gönderir.",
    "Model artık veriye sahiptir. Ya yeni bir tool ister (döngü sürer) ya da `stop_reason: end_turn` ile nihai "
    "metni üretir.",
])
P("`AiAgent::run()` metodu bu dört adımın birebir PHP karşılığıdır.")

# ================================================================ 2. FLOWCHART
H1("2. Flowchart (Akış Şeması)", brk=False)
P("Aşağıdaki şema, kullanıcının mesajı göndermesinden cevabın ekrana basılmasına kadar geçen **uçtan uca** "
  "akışı gösterir. Numaralar “3. Veri Akışı” bölümündeki adım numaralarıyla aynıdır. Sol kolon ana (mutlu) "
  "yolu, sağ üst kolon hata çıkışlarını ve yapılandırma/şema girdilerini, sağ alt kolon ise tool yürütme "
  "döngüsünü gösterir.")
callout("Kırmızı kutular hata çıkışlarıdır. Gri kesikli oklar yapılandırma veya şema girdisini, turuncu oklar "
        "tool döngüsünü gösterir. Turuncu dönüş oku, tool sonuçlarının eklendiği `$messages` dizisiyle bir "
        "sonraki tura geçildiğini anlatır.", title="Şema nasıl okunur?")
story.append(PageBreak())
story.append(Paragraph("2.1 Uçtan uca istek akışı", ST["H2"]))
story.append(Diagram(483, 716, paint_flow, scale=0.93))

H2("2.2 Sınıf / bağımlılık diyagramı")
P("Bu şema “kim kimi kullanıyor” sorusunu cevaplar. Ok yönü bağımlılık yönüdür: ok, kullanan sınıftan "
  "kullanılan sınıfa doğrudur. Düz oklar Service Container üzerinden enjekte edilen bağımlılıkları, kesikli "
  "oklar statik çağrıları gösterir.")
story.append(Diagram(483, 460, paint_deps, scale=1.0))
P("Diyagramdan çıkan önemli sonuçlar:")
BL([
    "**Bağımlılıklar tek yönlüdür ve döngü yoktur.** Controller → Ajan → (İstemci, Tool servisi) → (HTTP, Model). "
    "Alt katmanlar üst katmanları tanımaz. AiClient tool'lardan, ToolsService ise LLM'den habersizdir.",
    "**ToolSchema bir yapraktır.** Hiçbir şeye bağımlı değildir ama iki sınıf tarafından kullanılır. Tool "
    "listesinin “tek doğruluk kaynağı” (single source of truth) budur.",
    "**AiClient Anthropic'i tanıyan tek sınıftır.** Model sağlayıcısı değişirse etkilenen yer çoğunlukla burasıdır "
    "(ancak mesaj formatı Anthropic'e özgü olduğu için AiAgent de etkilenir; bkz. 6.6).",
])

H2("2.3 Döngü boyunca $messages dizisinin büyümesi")
P("Ajanın tüm durumu tek bir PHP dizisinde, `$messages` içinde tutulur. Her turda bu dizi büyür ve "
  "**tamamı** yeniden API'ye gönderilir (API durumsuzdur; modelin hafızası bu dizidir).")
code("""TUR 1  gönderilen  : [ user("ORD-1003 siparişinin durumu ne?") ]
       gelen yanıt : stop_reason = tool_use
                     content = [ tool_use(id=toolu_A, name=get_order_status,
                                          input={order_number:"ORD-1003"}) ]

       -> ToolsService::call("get_order_status", {order_number:"ORD-1003"})

TUR 2  gönderilen  : [ user("ORD-1003 siparişinin durumu ne?"),
                       assistant([ tool_use(id=toolu_A, ...) ]),          <- yanıt aynen eklendi
                       user([ tool_result(tool_use_id=toolu_A,
                                          content='{"status":"success",...}') ]) ]
       gelen yanıt : stop_reason = end_turn
                     content = [ text("ORD-1003 numaralı siparişiniz hazırlanıyor ...") ]

       -> return $response  ->  AiAgent::text()  ->  {"reply": "..."}""")

# ================================================================ 3. VERİ AKIŞI
H1("3. Veri Akışı")
H2("3.1 Adım adım istek yolculuğu")
P("Numaralar flowchart'taki kutularla eşleşir.")
NL([
    "**Tarayıcı.** `x-ai.chat` bileşeni, kullanıcı formu gönderdiğinde `fetch(endpoint, {method: 'POST'})` çağırır. "
    "Gövde `{\"message\": \"…\"}` şeklindedir. Header'lar: `Content-Type: application/json`, "
    "`Accept: application/json` ve meta etiketinden okunan `X-CSRF-TOKEN`. `endpoint`, Blade'de "
    "`route('ai.send')` ile üretilir.",
    "**Route.** `routes/web.php` içindeki `Route::post('/ai/agent/send', [AgentController::class, 'post'])` "
    "isteği controller action'ına bağlar.",
    "**web middleware grubu.** Route `web.php`'de olduğu için oturum ve CSRF korumasından geçer. Token geçersizse "
    "Laravel 419 döner; istek controller'a hiç ulaşmaz.",
    "**Doğrulama.** `AgentController::post()` önce `message` alanını doğrular. Hata varsa Laravel bir "
    "`ValidationException` fırlatır. İstek `Accept: application/json` taşıdığı için bu otomatik olarak "
    "**422** JSON'a (`{message, errors}`) çevrilir; chat bileşeni `error.message` alanını gösterir.",
    "**Bağımlılık çözümü.** Laravel, `post()` imzasındaki `AiAgent` tipini görür ve container ile oluşturur: "
    "önce `AiClient` ve `ToolsService`'i (ikisinin de constructor bağımlılığı yoktur), sonra bunlarla `AiAgent`'ı. "
    "`AiAgent::__construct` tool tanımlarını `ToolSchema::all()` ile bir kez yükler.",
    "**Ajan döngüsü başlar.** Controller `run([['role' => 'user', 'content' => $message]])` çağırır. "
    "`for` döngüsü en fazla 5 tur döner.",
    "**API isteği hazırlanır.** `AiClient::send()` payload'u kurar: `model` (config), `messages`, "
    "`max_tokens: 1024`, `system` (persona) ve `tools` (şemalar).",
    "**Anthropic çağrısı.** `Http::withHeaders([...])->timeout(30)->post(...)->throw()->json()`. 4xx/5xx yanıtlar "
    "`RequestException`'a dönüşür (controller → 502). Timeout ve bağlantı hataları `ConnectionException` "
    "fırlatır (controller → `Throwable` → 500).",
    "**Tool yürütme.** `stop_reason === 'tool_use'` ise modelin yanıtı `assistant` mesajı olarak eklenir. Her "
    "`tool_use` bloğu için `ToolsService::call($name, $input)` çağrılır. `call()` adı whitelist'e karşı kontrol eder.",
    "**İş mantığı.** İlgili metot (`get_customer_orders` / `get_order_status`) girdiyi normalize eder.",
    "**Veritabanı.** Eloquent sorgusu eager loading ile çalışır. Sonuç `formatOrder()` ile sade bir diziye "
    "dönüştürülür.",
    "**Sonuçların geri beslenmesi.** Her sonuç JSON string'e çevrilip `tool_result` bloğu yapılır. Tüm bloklar "
    "**tek bir** `user` mesajında `$messages`'a eklenir. Döngü 6. adıma döner.",
    "**Bitiş.** `stop_reason` artık `tool_use` değilse (tipik olarak `end_turn`) ham yanıt geri döner. 5 tur "
    "dolarsa ajan, aynı formatta sentetik bir yanıt üretir (`stop_reason: max_steps`).",
    "**Metne çevirme.** Controller `AiAgent::text($response)` ile tüm `text` bloklarını birleştirir. Sonuç boşsa "
    "“Bir cevap üretilemedi.” kullanılır.",
    "**Yanıt.** `{\"reply\": \"…\"}` JSON'u 200 ile döner. Bileşenin `extractReply()` fonksiyonu `reply` "
    "alanını okuyup asistan balonu olarak çizer.",
])

H2("3.2 Somut örnek: tek tool çağrılı soru")
callout("Aşağıdaki JSON'larda yapı gerçektir; id, tutar, tarih ve isim gibi değerler örnek amaçlıdır.",
        title="Not")
H4("(a) Tarayıcı → Laravel")
code("""POST /ai/agent/send
Content-Type: application/json
Accept: application/json
X-CSRF-TOKEN: 3kV...

{"message": "ORD-1003 siparişinin durumu ne?"}""")
H4("(b) AiClient → Anthropic (1. tur payload'u, kısaltılmış)")
code("""{
  "model": "<ANTHROPIC_MODEL>",
  "max_tokens": 1024,
  "system": "Sen bir e-ticaret mağazasının müşteri hizmetleri asistanısın. ...",
  "tools": [
    {"name": "get_customer_orders", "description": "...", "input_schema": {...}},
    {"name": "get_order_status",    "description": "...", "input_schema": {...}}
  ],
  "messages": [
    {"role": "user", "content": "ORD-1003 siparişinin durumu ne?"}
  ]
}""")
H4("(c) Anthropic → AiClient (1. tur yanıtı)")
code("""{
  "id": "msg_01...",
  "role": "assistant",
  "stop_reason": "tool_use",
  "content": [
    {"type": "tool_use", "id": "toolu_01A", "name": "get_order_status",
     "input": {"order_number": "ORD-1003"}}
  ],
  "usage": {"input_tokens": 912, "output_tokens": 58}
}""")
H4("(d) ToolsService::call('get_order_status', …) dönüşü")
code("""[
  'status' => 'success',
  'order'  => [
      'order_number' => 'ORD-1003',
      'order_status' => 'processing',
      'total_amount' => 1249.9,
      'notes'        => 'Hediye paketi',
      'created_at'   => '2026-10-05',
      'customer'     => 'Ayşe Demir',
  ],
]""")
H4("(e) 2. turda gönderilen messages dizisi")
code("""[
  {"role": "user", "content": "ORD-1003 siparişinin durumu ne?"},
  {"role": "assistant", "content": [
      {"type": "tool_use", "id": "toolu_01A", "name": "get_order_status",
       "input": {"order_number": "ORD-1003"}}]},
  {"role": "user", "content": [
      {"type": "tool_result", "tool_use_id": "toolu_01A", "is_error": false,
       "content": "{\\"status\\":\\"success\\",\\"order\\":{\\"order_number\\":\\"ORD-1003\\",
                   \\"order_status\\":\\"processing\\", ... ,\\"customer\\":\\"Ayşe Demir\\"}}"}]}
]""")
H4("(f) 2. tur yanıtı → Controller → Tarayıcı")
code("""// Anthropic: {"stop_reason": "end_turn",
//             "content": [{"type": "text", "text": "ORD-1003 numaralı sipariş ..."}]}

HTTP/1.1 200 OK
{"reply": "ORD-1003 numaralı sipariş Ayşe Demir'e ait ve şu an hazırlanıyor. Tutar: 1.249,90 TL."}""")

H2("3.3 Paralel / çok adımlı tool kullanımı")
P("Kullanıcı tek mesajda iki şey sorarsa (“Ahmet Yılmaz'ın siparişleri ve ORD-1003'ün durumu?”), model aynı "
  "yanıtta **iki** `tool_use` bloğu döndürebilir. `AiAgent` bu durumu doğal olarak destekler: `foreach` tüm "
  "blokları sırayla çalıştırır ve iki `tool_result`'ı **aynı** `user` mesajında gönderir. Bu, API'nin beklediği "
  "formattır: paralel tool çağrılarının sonuçları tek mesajda toplanmalıdır.")
P("Model ilk sonuca bakıp ikinci bir tool'a karar da verebilir (ör. önce müşteri arar, sonra belirli bir "
  "siparişi sorgular). Bu durumda her karar ayrı bir tur tüketir. `maxSteps = 5` sınırı bu zincirin uzunluğunu "
  "kısıtlar.")

H2("3.4 Hata akışları")
table([
    ["Durum", "Nerede yakalanır", "HTTP", "Kullanıcının gördüğü"],
    ["CSRF token yok/geçersiz", "web middleware (VerifyCsrfToken)", "419", "“CSRF token mismatch.” (Laravel mesajı)"],
    ["`message` boş, string değil, >2000 karakter", "`$request->validate()`", "422", "Doğrulama mesajı (ör. alan zorunlu)"],
    ["API anahtarı hatalı, model adı yanlış, rate limit, aşırı yük (401/400/429/529)",
     "`->throw()` → `RequestException` → controller", "502", "“AI servisine ulaşılamadı. Lütfen tekrar dene.”"],
    ["30 sn timeout, DNS/bağlantı hatası", "`ConnectionException` → `Throwable` dalı", "500",
     "“Beklenmeyen bir hata oluştu.”"],
    ["Kod hatası (TypeError, DB bağlantısı vb.)", "`Throwable` dalı", "500", "“Beklenmeyen bir hata oluştu.”"],
    ["Model bilinmeyen tool adı ister", "`ToolsService::call()` whitelist", "200",
     "Model hatayı `is_error` ile alır, kullanıcıya açıklar"],
    ["Müşteri/sipariş bulunamadı", "Tool metodu `status: error` döner", "200", "“… bulunamadı” (modelin ifadesiyle)"],
    ["5 turda cevap çıkmadı", "`AiAgent::run()` sonrası fallback", "200", "“Bu soruyu yanıtlamak için çok fazla adım gerekti…”"],
    ["Model boş metin döndürdü", "`AiAgent::text(...) ?: …`", "200", "“Bir cevap üretilemedi.”"],
], [140, 128, 34, 181])
P("Tasarım ilkesi: **İş seviyesindeki “olumsuz” sonuçlar (kayıt yok, belirsiz isim) modele veri olarak verilir, "
  "200 ile döner. Yalnızca altyapı arızaları HTTP hata koduna dönüşür.** Böylece model “bulunamadı” bilgisini "
  "kullanıcıya bağlamıyla birlikte, doğal bir dille aktarabilir.")

H2("3.5 Süre ve maliyet profili")
BL([
    "Her tur **bir** API çağrısıdır. Tipik soru 2 tur sürer: tool isteği + nihai cevap.",
    "Her çağrıda `system` prompt ve iki tool şeması **yeniden** gönderilir; geçmiş de her turda büyür. Token "
    "maliyeti turlarla birlikte artar.",
    "En kötü durumda 5 tur × 30 sn timeout = **150 sn**. Bu süre PHP-FPM'in `max_execution_time` değerini ve "
    "web sunucusu/proxy zaman aşımlarını aşabilir (bkz. 6.6 Bilinen sınırlamalar).",
    "`max_tokens: 1024` tek bir yanıtın uzunluğunu sınırlar. Kısa müşteri hizmetleri cevapları için yeterlidir.",
])

# ================================================================ 4. KLASÖR YAPISI
H1("4. Klasör Yapısı")
H2("4.1 İlgili dizin ağacı")
code("""exampleai/
|-- app/
|   |-- Http/
|   |   `-- Controllers/
|   |       |-- Controller.php               (boş abstract taban sınıf)
|   |       `-- Ai/
|   |           `-- AgentController.php      <- HTTP giriş noktası
|   |-- Schema/
|   |   `-- ToolSchema.php                   <- Modele sunulan tool sözleşmeleri
|   |-- Services/
|   |   `-- Ai/
|   |       |-- AiAgent.php                  <- Ajan döngüsü / orkestrasyon
|   |       |-- AiClient.php                 <- Anthropic HTTP istemcisi
|   |       `-- ToolsService.php             <- Tool uygulamaları (Eloquent)
|   `-- Models/
|       |-- Customer.php                     (hasMany Order)
|       `-- Order.php                        (belongsTo Customer)
|-- config/
|   `-- services.php                         ('anthropic' => key, model)
|-- database/migrations/
|   |-- 2026_10_12_000001_create_customers_table.php
|   `-- 2026_10_12_000002_create_orders_table.php
|-- resources/views/
|   |-- ai/agent.blade.php                   (sayfa: <x-ai.chat :endpoint=...>)
|   `-- components/ai/chat.blade.php         (sohbet UI + fetch)
`-- routes/
    `-- web.php                              (ai.agent, ai.send)""")

H2("4.2 Her klasörün görevi")
H3("app/Http/Controllers/Ai/")
P("**HTTP katmanı.** Dış dünyadan gelen isteği karşılar, doğrular ve iç servislere devreder. `Ai` alt "
  "klasörü, AI ile ilgili controller'ları diğer controller'lardan ayırır. Namespace `App\\Http\\Controllers\\Ai` "
  "olur (PSR-4: klasör yolu = namespace). İleride `ChatController` veya `AiAdminController` gibi sınıflar da "
  "buraya eklenir. Bu, **özellik (feature) bazlı gruplamanın** küçük bir uygulamasıdır.")
H3("app/Services/Ai/")
P("**Uygulama / domain servis katmanı.** Laravel'de varsayılan bir `Services` klasörü yoktur; bu bir "
  "topluluk konvansiyonudur. Amaç, controller'ı ince tutup iş mantığını HTTP'den bağımsız, yeniden "
  "kullanılabilir sınıflara taşımaktır. Buradaki sınıflar bir Artisan komutundan, bir queue job'undan veya "
  "testlerden de çağrılabilir; hiçbiri `Request` nesnesine bağımlı değildir. Composer'ın PSR-4 autoload'u "
  "sayesinde ekstra kayıt gerekmez; container sınıfları otomatik bulur.")
P("Klasördeki üç dosya, ajan mimarisinin üç temel rolünü temsil eder: **orkestratör** (AiAgent), **model "
  "erişimi** (AiClient) ve **araç uygulamaları** (ToolsService).")
H3("app/Schema/")
P("**Sözleşme / tanım katmanı.** Davranış değil, **veri tanımı** içerir. Tool şemaları hem modele gönderilen "
  "bir sözleşme hem de güvenlik whitelist'idir. Bu yüzden servislerden ayrı, kendi klasöründe tutulmuştur. "
  "Laravel standardında olmayan bir klasördür.")
callout("`App\\Schema` namespace'i, Laravel'in `Illuminate\\Support\\Facades\\Schema` facade'ı ile isim olarak "
        "benzerdir. Farklı namespace'lerde oldukları için çakışma olmaz. Yine de bir migration veya serviste "
        "ikisi birlikte import edilirse `use ... as ...` ile takma ad vermek gerekir.", kind="warn",
        title="İsim benzerliği uyarısı")
H3("Akışa dahil diğer klasörler")
BL([
    "`routes/web.php`: AI uç noktalarının URL'lerini ve route adlarını (`ai.agent`, `ai.send`) tanımlar.",
    "`config/services.php`: Anthropic anahtarı ve model adını `.env`'den okur. Kod `env()` yerine her zaman "
    "`config()` kullanır; böylece `php artisan config:cache` ile uyumludur.",
    "`app/Models/`: Tool'ların sorguladığı Eloquent modelleri.",
    "`resources/views/components/ai/`: Sohbet arayüzü. Endpoint, controller'ın döndürdüğü `{reply}` "
    "sözleşmesine göre yazılmıştır.",
])

# ================================================================ 5. DOSYA AÇIKLAMALARI
H1("5. Dosya Açıklamaları")
P("Bu bölüm her dosyayı “kod okumadan” anlaşılacak şekilde tanıtır. Satır satır inceleme 6. bölümdedir.")


def file_section(title, path, rows, methods):
    H2(title)
    story.append(file_bar(path))
    SP(4)
    table([["Başlık", "Açıklama"]] + rows, [120, 363])
    H4("Önemli metodlar / üyeler")
    table([["Metod", "Açıklama"]] + methods, [150, 333], mono_first=True)


file_section("5.1 AgentController", "app/Http/Controllers/Ai/AgentController.php", [
    ["Amaç", "AI asistanın HTTP kapısı. Sohbet sayfasını sunar ve mesaj uç noktasını sağlar."],
    ["Neden oluşturuldu?", "HTTP'ye özgü işleri (doğrulama, durum kodları, JSON, loglama) ajan mantığından "
     "ayırmak için. AiAgent HTTP'yi, controller ise LLM'i bilmez."],
    ["Hangi problemi çözüyor?", "Kullanıcı girdisinin güvenle alınması ve dış servis hatalarının kullanıcıya "
     "anlamlı, iç detay sızdırmayan mesajlarla dönmesi."],
    ["Sistemdeki görevi", "“İnce controller”: doğrula → ajanı çalıştır → sonucu/hatayı HTTP'ye çevir."],
    ["Kullananlar", "`routes/web.php` (`ai.agent` → `index`, `ai.send` → `post`). Dolaylı olarak "
     "`components/ai/chat.blade.php` (fetch ile)."],
    ["Kullandıkları", "`App\\Http\\Controllers\\Controller` (taban sınıf), `AiAgent`, `Request`, "
     "`RequestException`, `Log`, `Throwable`, `ai.agent` view'ı."],
], [
    ["index()", "`GET /ai/agent`. `resources/views/ai/agent.blade.php` view'ını döner. Mantık içermez."],
    ["post(Request, AiAgent)", "`POST /ai/agent/send`. Mesajı doğrular, `AiAgent::run()`'ı tek kullanıcı mesajıyla "
     "çağırır, API hatalarını 502'ye, diğer tüm hataları 500'e çevirir, başarıda `{reply}` döner."],
])

file_section("5.2 AiAgent", "app/Services/Ai/AiAgent.php", [
    ["Amaç", "Sistemin orkestratörü. Modelle tool'lar arasındaki çok adımlı konuşmayı yönetir."],
    ["Neden oluşturuldu?", "Tool-use protokolü tek bir API çağrısıyla bitmez: istek → tool → sonuç → tekrar istek. "
     "Bu döngünün, persona kurallarının ve adım sınırının tek bir yerde toplanması gerekir."],
    ["Hangi problemi çözüyor?", "Modelin tool isteklerini çalıştırıp sonuçları API'nin beklediği formatta geri "
     "beslemek, sonsuz döngüyü engellemek ve modelin veri uydurmasını (hallucination) system prompt ile "
     "kısıtlamak."],
    ["Sistemdeki görevi", "Controller ile alt servisler (AiClient, ToolsService) arasında koordinatör."],
    ["Kullananlar", "`AgentController` (`run()` ve statik `text()`)."],
    ["Kullandıkları", "`AiClient` (inject), `ToolsService` (inject), `ToolSchema` (statik), Laravel `collect()` helper."],
], [
    ["$system", "Persona ve davranış kuralları (Türkçe, tool dışı bilgi uydurma, durum çevirileri, TL)."],
    ["$tools", "`ToolSchema::all()` çıktısı; her API çağrısında modele gönderilir."],
    ["$maxSteps = 5", "Bir istekteki en fazla API turu sayısı."],
    ["__construct(AiClient, ToolsService)", "Constructor property promotion ile bağımlılıkları alır, tool listesini yükler."],
    ["run(array $messages): array", "Ajan döngüsü. Son Anthropic yanıtını (veya aynı formatta sentetik bir yanıtı) döner."],
    ["static text(array $response): string", "Yanıttaki tüm `text` bloklarını satır sonuyla birleştirir."],
])

file_section("5.3 AiClient", "app/Services/Ai/AiClient.php", [
    ["Amaç", "Anthropic Messages API'ye tek bir HTTP isteği atan ince adaptör (gateway)."],
    ["Neden oluşturuldu?", "URL, header, API versiyonu, model, `max_tokens` ve timeout gibi sağlayıcıya özgü "
     "ayrıntıları tek bir yerde toplamak için."],
    ["Hangi problemi çözüyor?", "API versiyonu yükselince, model değişince veya timeout ayarlanınca tek bir "
     "dosyanın değişmesi yeter. Testlerde `Http::fake()` ile gerçek ağa çıkmadan sahte yanıt verilebilir."],
    ["Sistemdeki görevi", "Altyapı katmanı. İş mantığı içermez; ne gönderildiğini değil, *nasıl* gönderildiğini bilir."],
    ["Kullananlar", "`AiAgent`."],
    ["Kullandıkları", "`Illuminate\\Support\\Facades\\Http`, `config('services.anthropic.*')`."],
], [
    ["send(array $messages, string $system = '', array $tools = []): array",
     "Payload'u kurar, boş `system`/`tools` alanlarını göndermez, isteği atar. HTTP hatasında exception fırlatır; "
     "başarıda JSON'u dizi olarak döner."],
])

file_section("5.4 ToolsService", "app/Services/Ai/ToolsService.php", [
    ["Amaç", "Modelin istediği tool'ları gerçekten çalıştıran katman (ajanın “elleri”)."],
    ["Neden oluşturuldu?", "Model veritabanına doğrudan erişemez ve erişmemelidir. Erişim, sınırları net, "
     "denetlenebilir PHP metotlarıyla sağlanır."],
    ["Hangi problemi çözüyor?", "Güvenli dinamik dispatch (whitelist), modelden gelen girdinin normalize "
     "edilmesi, verinin modele uygun sade bir formata çevrilmesi ve hataların veri olarak dönmesi."],
    ["Sistemdeki görevi", "Domain/veri erişim katmanı. LLM'den habersizdir; isim + girdi alır, dizi döner."],
    ["Kullananlar", "`AiAgent::run()`."],
    ["Kullandıkları", "`ToolSchema` (whitelist), `App\\Models\\Customer`, `App\\Models\\Order`."],
], [
    ["call(string $name, array $input): array", "Tek giriş noktası. Adı whitelist ve `method_exists` ile doğrular, "
     "ilgili metodu dinamik olarak çağırır."],
    ["get_customer_orders(array $input): array", "İsme göre (LIKE) en fazla 5 müşteri ve siparişlerini, sipariş "
     "sayısı ve iptaller hariç toplam harcamayla döner."],
    ["get_order_status(array $input): array", "Sipariş numarasıyla tek siparişi ve müşteri adını döner. “1001” "
     "girdisini “ORD-1001”e tamamlar."],
    ["private formatOrder(Order): array", "Her iki tool'un ortak sipariş formatı."],
])

file_section("5.5 ToolSchema", "app/Schema/ToolSchema.php", [
    ["Amaç", "Modele sunulan tool sözleşmelerini (ad, açıklama, girdi JSON Schema'sı) tanımlar."],
    ["Neden oluşturuldu?", "Anthropic API her istekte `tools` parametresinde bu tanımları bekler. Model hangi "
     "tool'u ne zaman ve hangi parametreyle çağıracağına yalnızca bu açıklamalara bakarak karar verir."],
    ["Hangi problemi çözüyor?", "Tool listesi için tek doğruluk kaynağı sağlar: aynı liste hem modele gönderilir "
     "hem de ToolsService'te whitelist olarak kullanılır. İkisi birbirinden kopamaz."],
    ["Sistemdeki görevi", "Sözleşme / yapılandırma. Davranış içermez."],
    ["Kullananlar", "`AiAgent::__construct()`, `ToolsService::call()`."],
    ["Kullandıkları", "Hiçbir şey (saf PHP dizisi)."],
], [
    ["static all(): array", "İki tool tanımını döner: `get_customer_orders` (girdi: `customer_name`) ve "
     "`get_order_status` (girdi: `order_number`)."],
])

# ================================================================ 6. KOD ANALİZİ
H1("6. Kod Analizleri")
P("Her dosya, gerçek satır numaralarıyla parça parça incelenir. Her parçanın altında kodun **ne yaptığı** ve "
  "daha önemlisi **neden böyle yazıldığı** açıklanır.")

# ---- 6.1 AgentController
C = "app/Http/Controllers/Ai/AgentController.php"
H2("6.1 AgentController.php")
snip(C, 3, 10, [
    "Namespace klasör yapısıyla birebir aynıdır (PSR-4). Composer bu sayede sınıfı ek kayıt olmadan bulur.",
    "`RequestException` özellikle import edilmiştir, çünkü **API'nin hata döndürmesi** ile **diğer tüm hatalar** "
    "ayrı ele alınır. `Throwable` ise `Exception`'dan daha geniştir: PHP'nin `Error` sınıflarını (TypeError, "
    "Error vb.) da yakalar. Böylece hiçbir hata kullanıcıya ham stack trace olarak sızmaz.",
])
snip(C, 12, 16, [
    "`extends Controller`: Laravel 11+ ile taban `Controller` sınıfı boş bir abstract sınıftır. Miras almak, "
    "ileride tüm controller'lara ortak bir davranış eklenebilmesi için tutarlılık sağlar.",
    "`index()` yalnızca view döner. Sayfa render'ı ile mesaj işleme ayrı action'lardadır. Böylece `GET` isteği "
    "AiAgent'ı oluşturma maliyetine (container çözümlemesi) hiç girmez.",
])
snip(C, 21, 21, [
    "**Method injection (Dependency Injection).** `AiAgent` parametresi Laravel'in Service Container'ı tarafından "
    "otomatik oluşturulur (autowiring). Container reflection ile `AiAgent`'ın constructor'ına bakar, `AiClient` ve "
    "`ToolsService`'i oluşturur, onları da enjekte eder.",
    "**Neden DI?** (1) Controller, AiAgent'ın neye bağımlı olduğunu bilmek zorunda kalmaz. Yarın AiAgent'a bir "
    "`Logger` bağımlılığı eklense controller değişmez. (2) Testte `$this->mock(AiAgent::class, ...)` ile ajan "
    "sahtesiyle değiştirilebilir; gerçek API'ye gidilmez.",
    "**Neden constructor yerine method injection?** Bağımlılığa yalnızca `post()` ihtiyaç duyar. Constructor'a "
    "koymak `index()` çağrısında da gereksiz yere nesne oluşturur.",
])
snip(C, 22, 25, [
    "**Validasyon neden gerekli?** `required`: boş mesajla API'ye para harcayan bir çağrı yapılmasını engeller. "
    "`string`: `message[]=x` gibi dizi girdileri reddeder; aksi halde Anthropic'e geçersiz `content` gider. "
    "`max:2000`: token maliyetini ve kötüye kullanımı (çok uzun prompt, prompt injection yüzeyi) sınırlar.",
    "İstek `Accept: application/json` taşıdığı için doğrulama hatası redirect yerine otomatik olarak **422 JSON** "
    "olur. Chat bileşeni bu JSON'daki `message` alanını hata balonu olarak gösterir.",
    "`$request->message` sihirli property erişimidir (`$request->input('message')` ile eşdeğer). Daha açık bir "
    "alternatif: `$message = $request->validate([...])['message'];`. Bu yalnızca doğrulanmış veriyi kullanır.",
])
snip(C, 27, 33, [
    "Ajan, Anthropic formatında tek elemanlı bir mesaj dizisiyle başlatılır. `content` düz string verilebilir; "
    "API bunu tek bir `text` bloğu olarak yorumlar.",
    "Geçmiş eklenmez, yani her istek bağımsızdır (stateless). Çok turlu bir sohbet için frontend'in tüm geçmişi "
    "göndermesi ya da sunucunun oturumda/DB'de saklaması gerekir.",
])
snip(C, 34, 37, [
    "`RequestException`, AiClient'taki `->throw()` tarafından 4xx/5xx yanıtlarda fırlatılır. Loga hem **status** "
    "hem **body** yazılır. Anthropic hata gövdesi (`{type: 'error', error: {type, message}}`) teşhis için kritiktir: "
    "401 geçersiz anahtar, 400 yanlış model adı, 429 rate limit, 529 aşırı yük.",
    "Kullanıcıya genel bir mesaj döner; API detayları (anahtar hatası vb.) sızdırılmaz. **502 Bad Gateway** "
    "anlamsal olarak doğrudur: sunucumuz çalışıyor, ama arkasındaki (upstream) servis başarısız oldu.",
])
snip(C, 38, 41, [
    "Diğer her şey 500 olur. `['exception' => $e]` bağlamı, Laravel log'unda tam stack trace'in yazılmasını sağlar.",
    "**Dikkat:** Zaman aşımı ve bağlantı hataları `Illuminate\\Http\\Client\\ConnectionException` fırlatır. Bu "
    "sınıf `RequestException` **değildir**, dolayısıyla bu dala düşer ve kullanıcı 502 yerine 500 / “Beklenmeyen "
    "bir hata” görür. Ayrı bir `catch (ConnectionException $e)` eklemek davranışı daha tutarlı yapar.",
])
snip(C, 44, 46, [
    "Ham Anthropic yanıtı `AiAgent::text()` ile düz metne çevrilir. `?:` (Elvis) operatörü boş string durumunda "
    "yedek mesaja düşer. Bu durum, örneğin `max_tokens` sınırına metin üretilmeden takılan bir yanıtta ortaya çıkar.",
    "Dönüş şekli `{reply}`, chat bileşenindeki `extractReply()` fonksiyonunun ilk kontrol ettiği alandır "
    "(`typeof data?.reply === 'string'`). Backend ve frontend bu küçük sözleşmeyle bağlıdır.",
])

# ---- 6.2 AiAgent
A = "app/Services/Ai/AiAgent.php"
H2("6.2 AiAgent.php")
snip(A, 1, 7, [
    "`ToolSchema` doğrudan import edilir; tool listesi enjekte edilmez, statik olarak okunur. Liste sabit ve "
    "durumsuz olduğu için bu kabul edilebilir bir sadeleştirmedir.",
    "Sınıf bir **interface** uygulamaz. Tek bir ajan türü olduğu için soyutlama şu an gereksizdir (YAGNI). "
    "Ne zaman gerekeceği 6.6'da tartışılmıştır.",
])
snip(A, 9, 13, [
    "**System prompt**, modelin kimliğini ve kurallarını belirler. Her cümlenin bir amacı vardır:",
])
BL([
    "*“tool'larla öğren; uydurma”* → Hallucination'a karşı ana savunma. Model veritabanındaki bilgiyi ancak tool "
    "sonucundan bilebilir.",
    "*“Bir kayıt bulunamazsa açıkça söyle”* → Tool'ların `status: error` dönüşlerinin nasıl ele alınacağını tarif eder.",
    "*“Birden fazla müşteri eşleşirse …”* → `get_customer_orders` LIKE ile 5'e kadar müşteri döndürebildiği için "
    "gereken belirsizlik giderme kuralı. Kod ile prompt burada birbirini tamamlar.",
    "*Durum çevirileri* → Veritabanı enum'u İngilizcedir (`pending` …). Çeviri kodda değil promptta yapılır; "
    "böylece tool çıktısı ham ve dilden bağımsız kalır.",
    "*“TL, Türkçe, kısa ve net”* → Ton ve format; `max_tokens: 1024` ile de uyumludur.",
])
P("Prompt'un config yerine kodda tutulması, prompt değişikliklerinin kodla birlikte versiyonlanmasını sağlar. "
  "Prompt'u değiştirmek bir kod değişikliğidir; review ve test sürecinden geçer.")
snip(A, 15, 25, [
    "**Constructor property promotion (PHP 8).** `private AiClient $aiClient` hem property'yi tanımlar hem atamayı "
    "yapar. Daha az tekrar ve daha okunur bir kod elde edilir.",
    "**Constructor injection.** Ajanın bu iki servis olmadan çalışamayacağı imzadan bellidir (açık bağımlılık). "
    "İkisi de somut sınıftır ve constructor'larında parametre yoktur. Bu yüzden container herhangi bir "
    "`bind()` kaydı olmadan onları otomatik oluşturur.",
    "`$maxSteps = 5`: Tipik soru 1–2 tool turu ister; 5, birden fazla tool zinciri için pay bırakırken maliyeti, "
    "gecikmeyi ve olası bir modelin aynı tool'u tekrar tekrar çağırma döngüsünü sınırlar.",
    "`$this->tools = ToolSchema::all()` nesne başına bir kez çalışır. Her turda yeniden oluşturulmaz.",
])
snip(A, 30, 37, [
    "`run()` **string değil dizi döner**: ham Anthropic yanıtı. Böylece çağıran taraf `stop_reason`, `usage` "
    "(token sayıları) gibi alanlara erişebilir. Metne çevirme işi ayrı bir sorumluluk olarak `text()`'e bırakılmıştır.",
    "Döngü sayaçlıdır (`for`), `while(true)` değildir; sınır yapısal olarak garanti altındadır.",
    "`($response['stop_reason'] ?? null) !== 'tool_use'`: `end_turn`, `max_tokens`, `stop_sequence`, `refusal` gibi "
    "**tool dışındaki tüm durumlar** “bitti” sayılır. `?? null` beklenmedik bir yanıtta “undefined index” "
    "uyarısını engeller (savunmacı programlama).",
])
snip(A, 39, 43, [
    "Modelin yanıtı **değiştirilmeden** `assistant` mesajı olarak eklenir. Bu API'nin zorunlu bir kuralıdır: "
    "`tool_result` blokları bir önceki assistant mesajındaki `tool_use` id'lerine referans verir. Blokları "
    "filtrelemek veya yeniden yazmak protokolü bozar ve API 400 döndürür.",
])
snip(A, 45, 61, [
    "`content` dizisinde metin blokları da olabilir (model tool çağırmadan önce “Kontrol ediyorum…” diyebilir). "
    "`continue` yalnızca `tool_use` bloklarını işler.",
    "`(array) ($block['input'] ?? [])`: Input yoksa veya boş bir JSON nesnesi (`{}`) gelirse bile ToolsService'in "
    "`array` tip ipucu (type hint) TypeError fırlatmaz.",
    "`tool_use_id => $block['id']`: Her sonucu doğru isteğe bağlar. Paralel çağrılarda eşleşme buna dayanır.",
    "`json_encode(..., JSON_UNESCAPED_UNICODE)`: Tool sonucu API'ye string olarak verilir. Bu bayrak sayesinde "
    "“Ayşe” `Ay\\u015fe` olmaz; hem okunur kalır hem de daha az token harcar.",
    "`is_error`: ToolsService'in `status: error` sözleşmesi API'nin `is_error` alanına çevrilir. Model böylece "
    "sonucun başarısız olduğunu kesin olarak bilir.",
])
snip(A, 63, 67, [
    "Tüm `tool_result` blokları **tek bir** `user` mesajında gönderilir. API, paralel tool çağrılarının "
    "sonuçlarını tek mesajda bekler; ayrı ayrı mesajlar hem kurala aykırıdır hem de modelin paralel tool "
    "kullanma eğilimini bozar. Ardından döngü başa döner ve büyümüş `$messages` ile yeni bir istek atılır.",
])
snip(A, 69, 74, [
    "Adım sınırı aşılırsa exception fırlatılmaz. Bunun yerine **Anthropic yanıtıyla aynı şekle sahip** sentetik bir "
    "dizi döner (`stop_reason` + `content[text]`). Bu bir tür *Null Object* yaklaşımıdır: controller'ın özel bir "
    "durumu ele alması gerekmez, `text()` aynen çalışır ve kullanıcı yönlendirici bir mesaj görür.",
])
snip(A, 80, 86, [
    "Laravel Collection zinciri: `where('type', 'text')` metin bloklarını filtreler, `pluck('text')` metinleri "
    "çeker, `implode(\"\\n\")` birleştirir. Model bir yanıtta birden fazla metin bloğu üretebilir (ör. tool öncesi "
    "ve sonrası). Bu metot hepsini birleştirir.",
    "**Neden statik?** Saf bir fonksiyondur: nesne durumuna ihtiyaç duymaz, aynı girdiye hep aynı çıktıyı verir. "
    "Ajan örneğine sahip olmayan bir yerden (ör. bir test) de çağrılabilir.",
])

# ---- 6.3 AiClient
K = "app/Services/Ai/AiClient.php"
H2("6.3 AiClient.php")
snip(K, 1, 8, [
    "`Http` facade, Laravel'in Guzzle tabanlı HTTP istemcisidir. Facade kullanımı, testlerde `Http::fake()` ile "
    "tüm dış çağrıların sahteleriyle değiştirilebilmesini sağlar.",
    "`send()` imzasında `system` ve `tools` opsiyoneldir. İstemci böylece tool'suz basit tek seferlik çağrılar "
    "(ör. bir özetleme özelliği) için de yeniden kullanılabilir. Ajana özgü hiçbir şey içermez.",
])
snip(K, 10, 14, [
    "`model` **config'ten** okunur, kodda sabit yazılı değildir. Model yükseltmesi yalnızca `.env` değişikliğiyle "
    "yapılır. Kod `env()`'i doğrudan çağırmaz, `config()` kullanır; bu, config cache ile uyumluluk için Laravel'in "
    "önerdiği yoldur.",
    "`max_tokens` Messages API'de **zorunlu** bir parametredir. 1024, kısa müşteri hizmetleri cevapları için yeterli "
    "bir üst sınırdır ve maliyeti de kontrol eder.",
])
snip(K, 16, 21, [
    "Boş `system` ve boş `tools` alanları payload'a hiç eklenmez. API boş değerlere doğrulama hatası "
    "verebileceği için alanı hiç göndermemek hem daha temiz hem daha güvenlidir.",
])
snip(K, 23, 29, [
    "`x-api-key`: Anthropic kimlik doğrulama header'ı. Değer config'ten gelir, koda veya loglara yazılmaz.",
    "`anthropic-version: 2023-06-01`: Zorunlu header. API davranışını belirli bir sözleşme sürümüne sabitler. "
    "Böylece Anthropic tarafındaki değişiklikler mevcut kodu habersizce bozmaz.",
    "`timeout(30)`: Tek bir çağrının en fazla 30 sn sürmesine izin verir (Laravel'in varsayılanı da 30 sn'dir; "
    "açıkça yazmak niyeti belgeler).",
    "`post($url, $payload)`: Dizi payload otomatik olarak JSON'a çevrilir ve `Content-Type: application/json` "
    "eklenir.",
    "`->throw()`: **Kritik satır.** Laravel HTTP istemcisi 4xx/5xx yanıtlarda varsayılan olarak exception "
    "fırlatmaz. `throw()` olmasaydı hata gövdesi normal yanıt gibi `json()` ile dönerdi. `stop_reason` olmadığı için "
    "AiAgent bunu “bitti” sayar, kullanıcı da sessizce “Bir cevap üretilemedi.” görürdü. `throw()` hatayı "
    "görünür kılar ve controller'ın 502 dalına yönlendirir.",
    "`->json()`: Yanıt gövdesini ilişkisel PHP dizisine çevirir. Sistemin geri kalanı bu diziyle çalışır.",
])
callout("Retry yok: 429/529 gibi geçici hatalar için `->retry(2, 500, fn ($e) => ...)` eklenebilir. Interface "
        "yok: sağlayıcı değiştirmek veya testte sahte istemci kullanmak için bir `LlmClient` interface'i ve "
        "`AppServiceProvider` içinde binding eklenebilir. Şu an `Http::fake()` test ihtiyacını karşılar.",
        kind="warn", title="Bilinçli olarak eklenmemiş özellikler")

# ---- 6.4 ToolsService
T = "app/Services/Ai/ToolsService.php"
H2("6.4 ToolsService.php")
snip(T, 1, 10, [
    "Servis yalnızca modelleri ve `ToolSchema`'yı import eder; LLM, HTTP veya AiClient ile hiçbir bağı yoktur. "
    "Bu nedenle bir Artisan komutundan veya testten doğrudan çağrılabilir.",
])
snip(T, 14, 23, [
    "**Güvenli dinamik dispatch.** `$this->{$name}($input)` ifadesi, string olarak gelen ismi metod çağrısına çevirir. "
    "Böylece yeni bir tool eklemek için `switch`/`match` güncellemek gerekmez. Ancak isim **modelden**, yani "
    "dolaylı olarak kullanıcıdan gelir. Prompt injection ile model `call`, `formatOrder` veya `__construct` gibi bir "
    "isim üretmeye zorlanabilir.",
    "**İki katmanlı kontrol bunu engeller:** (1) `in_array($name, $allowed, true)` yalnızca ToolSchema'daki adlara "
    "izin verir. `true` parametresi katı (strict) karşılaştırma yaparak tip hokkabazlığını önler. (2) "
    "`method_exists` ise şemaya eklenip ToolsService'e henüz yazılmamış bir tool için PHP fatal error yerine "
    "kontrollü bir hata döndürür.",
    "Hata durumunda exception değil, sözleşmeye uygun bir dizi döner. AiAgent bunu `is_error: true` ile modele iletir.",
])
callout("Metod adları `get_customer_orders` gibi snake_case'tir. Bu, PSR-1'in camelCase önerisine aykırıdır ama "
        "bilinçlidir: **tool adı = metod adı** konvansiyonu dinamik dispatch'in temelidir. Bir tool'un adını "
        "değiştirirken iki yeri (ToolSchema `name` ve metod adı) birlikte değiştirmek gerekir.",
        title="Konvansiyon: snake_case metodlar")
snip(T, 28, 34, [
    "**Girdi normalizasyonu.** `input_schema` modelden `customer_name` beklese de model çıktısı %100 garanti "
    "değildir: alan eksik, `null` veya sayı olabilir. `?? ''` eksik alanı, `(string)` tip dönüşümünü, `trim()` "
    "boşlukları ele alır. Boş isim, bütün müşterileri döndürecek bir `LIKE '%%'` sorgusunu engeller.",
])
snip(T, 36, 43, [
    "`where('name', 'like', \"%{$customerName}%\")`: Kısmi eşleşme. “Mehmet” tüm Mehmet'leri, “Yılmaz” tüm "
    "Yılmaz'ları bulur. Eloquent parametre binding kullanır; **SQL injection'a karşı güvenlidir**. Ancak girdideki "
    "`%` ve `_` karakterleri escape edilmez ve joker karakter gibi davranır (küçük bir doğruluk sorunu, güvenlik "
    "sorunu değil).",
    "`with(['orders' => fn ($q) => $q->latest()])`: **Eager loading** ile sınırlandırılmış ilişki. Siparişler en "
    "yeniden eskiye sıralanır. 5 müşteri için 1 + 1 = 2 sorgu çalışır; eager loading olmasaydı N+1 problemiyle "
    "6 sorgu çalışırdı.",
    "`limit(5)`: Hem tool açıklamasındaki “en fazla 5” sözünü tutar hem de modele gönderilen veri miktarını (token) "
    "sınırlar.",
])
snip(T, 45, 56, [
    "`match_count`: Modelin belirsizlik kuralını (“birden fazla müşteri eşleşirse sor”) uygulamasını kolaylaştırır.",
    "`total_spent`: **İş kuralı** olarak iptal edilen siparişler hariç tutulur. Hesaplama yüklenmiş koleksiyon "
    "üzerinde yapılır, ek sorgu gerekmez.",
    "`(float)` dönüşümü: `Order` modelinde `total_amount` `decimal:2` cast'ine sahiptir ve PHP'de **string** döner "
    "(`\"1249.90\"`). JSON'da sayı olarak görünmesi için float'a çevrilir.",
    "Telefon (`phone`) bilinçli olarak modele gönderilmez (veri minimizasyonu). E-posta ve şehir ise gönderilir. "
    "Kişisel verinin üçüncü taraf bir LLM'e iletildiği unutulmamalıdır (bkz. 6.6).",
])
snip(T, 62, 81, [
    "`strtoupper(trim(...))`: “ord-1003 ” → “ORD-1003”. `ctype_digit`: Kullanıcı sadece “1003” yazarsa önek "
    "eklenir. Tool şeması `ORD-` formatını istese de servis **toleranslıdır**: modelin veya kullanıcının küçük "
    "format hataları başarısız sorguya yol açmaz.",
    "`Order::with('customer')`: Müşteri adı için ikinci sorgu eager loading ile yapılır. `order_number` "
    "migration'da `unique` olduğu için indekslidir; arama hızlıdır.",
    "Hata mesajı aranan numarayı içerir. Model “ORD-1003 numaralı sipariş bulunamadı” bilgisini doğrudan "
    "kullanıcıya aktarabilir.",
    "`$this->formatOrder($order) + ['customer' => ...]`: PHP **dizi birleşimi (`+`)** operatörü. Ortak formatı "
    "tekrar yazmadan tek bir alan ekler.",
])
snip(T, 83, 92, [
    "**Neden private ortak formatlayıcı?** İki tool aynı sipariş şeklini döndürür. Model tutarlı alan adlarıyla "
    "çalışır, format tek bir yerden değişir. `private` olması onu dış dünyadan gizler (zaten whitelist'te de yoktur).",
    "`'order_status'` anahtarı bilinçlidir: Tool'un üst seviye `status` alanı (`success`/`error`) ile **isim "
    "çakışmasını** önler. Model “işlem durumu” ile “sipariş durumu”nu karıştırmaz.",
    "`created_at?->toDateString()`: Nullsafe operatör, `created_at` boşsa hata vermez. Saat bilgisi atılır; daha "
    "az token harcanır ve müşteri hizmetleri için gün yeterlidir.",
])

# ---- 6.5 ToolSchema
S = "app/Schema/ToolSchema.php"
H2("6.5 ToolSchema.php")
snip(S, 1, 10, [
    "Sınıfın tek işi bir dizi döndürmektir. Durum (state) tutmadığı için statik metod uygundur. Neden `const` "
    "değil de metod? Metod, ileride tanımların dinamik üretilmesine (ör. çeviri, config'e göre tool açma/kapama) "
    "çağıranları değiştirmeden izin verir.",
])
snip(S, 12, 28, [
    "`name`: ToolsService'teki metod adıyla **birebir aynı olmak zorundadır** (dinamik dispatch sözleşmesi).",
    "`description`: Model tool seçimini neredeyse tamamen bu metne bakarak yapar. Açıklama dört şeyi söyler: ne "
    "döndürür, **ne zaman** kullanılmalı, nasıl arar (ad/soyad, en fazla 5) ve **ne zaman kullanılmamalı** (“sipariş "
    "numarası için `get_order_status` kullanın”). Bu sonuncusu, iki tool arasındaki yanlış seçimleri ciddi ölçüde "
    "azaltır. Anthropic de ayrıntılı açıklamaları önerir.",
    "`input_schema`: Standart **JSON Schema**. `type: object`, `properties` içindeki her alanın açıklaması ve "
    "örnekleri, modelin doğru formatta argüman üretmesine yardım eder. `required` alanı modelin parametreyi "
    "atlamamasını sağlar. Yine de ToolsService savunmacı davranır (bkz. 6.4).",
])
snip(S, 29, 44, [
    "İkinci tool aynı deseni izler. `order_number` açıklamasındaki **örnek format** (`ORD-1001`) modeli doğru "
    "biçime yönlendirir. Açıklamadaki durum listesi (`pending, processing, …`) modelin çıktıyı yorumlamasına "
    "yardım eder; Türkçe karşılıklar ise system prompt'tadır.",
])

# ---- 6.6 Çapraz konular
H2("6.6 Çapraz konular ve tasarım değerlendirmesi")
H3("Dependency Injection: nerede, neden?")
table([
    ["Yer", "Tür", "Gerekçe"],
    ["`AgentController::post(…, AiAgent $aiAgent)`", "Method injection",
     "Bağımlılık sadece bu action'da gerekir; testte mock'lanabilir."],
    ["`AiAgent::__construct(AiClient, ToolsService)`", "Constructor injection",
     "Ajanın her işleminde gerekli; zorunlu bağımlılıklar imzada açıkça görünür."],
    ["`ToolSchema::all()`", "Statik çağrı (DI değil)",
     "Durumsuz, sabit veri; enjekte etmenin getirisi düşük."],
    ["`Http`, `Log`, `config()`", "Facade / helper",
     "Laravel'in test edilebilir facade'ları (`Http::fake`, `Log::spy`)."],
], [175, 100, 208])
P("Hiçbir `bind()` / `singleton()` kaydı yoktur. Tüm sınıflar somut (concrete) ve parametresiz constructor "
  "zincirine sahip olduğu için Laravel bunları **sıfır yapılandırmayla** otomatik çözer (autowiring).")
H3("Interface kullanımı")
P("Bu modülde interface **yoktur**. Tek bir LLM sağlayıcısı ve tek bir tool seti varken soyutlama eklemek "
  "fayda sağlamadan karmaşıklık ekler (YAGNI). Aşağıdaki durumlarda interface eklemek mantıklı hale gelir:")
BL([
    "Birden fazla model sağlayıcısı (ör. Anthropic + başka bir sağlayıcı) desteklenecekse veya ortama göre "
    "değişecekse,",
    "AiAgent'ı testte, HTTP katmanını sahtelemek yerine tamamen sahte bir istemciyle test etmek istenirse.",
])
code("""// Örnek (projede YOK, öneridir)
interface LlmClient {
    public function send(array $messages, string $system = '', array $tools = []): array;
}
class AiClient implements LlmClient { /* ... */ }

// AppServiceProvider::register()
$this->app->bind(LlmClient::class, AiClient::class);

// AiAgent constructor'ında AiClient yerine LlmClient tip ipucu kullanılır.""")
callout("Mesaj formatı (`tool_use`, `tool_result`, `stop_reason`) Anthropic'e özgüdür ve AiAgent bu formata "
        "doğrudan bağımlıdır. Gerçek bir sağlayıcı bağımsızlığı yalnızca bir interface ile değil, ortak bir "
        "mesaj modeline dönüşüm katmanıyla sağlanır.", title="Önemli")
H3("Trait kullanımı")
P("Bu modülde trait **yoktur** ve bu doğru bir tercihtir. Trait'ler, birbirinden bağımsız birden fazla sınıfın "
  "aynı davranışı paylaşması gerektiğinde kullanılır. Burada her sınıfın davranışı kendine özgüdür. Ortak "
  "kullanılan tek parça (`formatOrder`) yalnızca ToolsService içinde gerektiği için private metot olarak kalmıştır. "
  "Trait eklemek bağımlılıkları gizler ve “bu metod nereden geliyor?” sorusunu zorlaştırır. İleride çok sayıda "
  "tool sınıfı olursa ortak yanıt formatı (`success()`/`error()` yardımcıları) için bir trait düşünülebilir.")
H3("Güvenlik değerlendirmesi")
table([
    ["Konu", "Mevcut durum"],
    ["CSRF", "Var. Route `web` grubunda, bileşen `X-CSRF-TOKEN` gönderiyor."],
    ["Girdi doğrulama", "Var. `required|string|max:2000`."],
    ["Tool whitelist", "Var. Model yalnızca şemadaki iki tool'u çalıştırabilir."],
    ["SQL injection", "Korunuyor. Eloquent parametre binding kullanıyor."],
    ["Hata detayı sızıntısı", "Korunuyor. Kullanıcıya genel mesaj, detay log'a yazılıyor."],
    ["API anahtarı", "`.env` → config. Kodda ve log'da yok."],
    ["**Kimlik doğrulama / yetki**", "**Yok.** `/ai/agent` ve `/ai/agent/send` herkese açık. Siteye erişen herkes "
     "müşteri ad/e-posta/sipariş verisini sorgulayabilir ve API kredisi harcayabilir. `auth` middleware'i önerilir."],
    ["**Rate limiting**", "**Yok.** `throttle:…` middleware'i ile kullanıcı/IP başına sınır önerilir (maliyet koruması)."],
    ["Kişisel veri (KVKK)", "Müşteri adı, e-posta, şehir ve sipariş verisi üçüncü taraf LLM'e gönderiliyor. "
     "Hukuki değerlendirme ve gerekirse veri minimizasyonu yapılmalı."],
], [120, 363])
H3("Bilinen sınırlamalar")
BL([
    "**Sohbet geçmişi yok:** Takip soruları bağlamı kaybeder.",
    "**Uzun istek süresi:** En kötü durumda ~150 sn (5 × 30 sn). PHP/web sunucusu zaman aşımları önce tetiklenebilir. "
    "Streaming yok; kullanıcı yanıt tamamlanana kadar “yazıyor…” görür.",
    "**ConnectionException 500'e düşüyor:** Timeout, “AI servisine ulaşılamadı” (502) yerine “Beklenmeyen hata” "
    "(500) gösterir.",
    "**`max_tokens` kesilmesi:** `stop_reason: max_tokens` durumunda kısmi metin, uyarı yapılmadan nihai cevap "
    "olarak gösterilir.",
    "**`.env.example`'da Anthropic değişkenleri yok:** Yeni bir kurulumda `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` "
    "eksik kalırsa API 401/400 döner (kullanıcı 502 görür).",
    "**LIKE joker karakterleri** (`%`, `_`) escape edilmiyor.",
    "**Test yok:** `tests/` altında yalnızca varsayılan örnek testler var.",
])
H3("Önerilen test iskeleti")
code("""// tests/Feature/AiAgentTest.php (öneri)
Http::fake([
    'api.anthropic.com/*' => Http::sequence()
        ->push(['stop_reason' => 'tool_use', 'content' => [[
            'type' => 'tool_use', 'id' => 'toolu_1', 'name' => 'get_order_status',
            'input' => ['order_number' => 'ORD-1001'],
        ]]])
        ->push(['stop_reason' => 'end_turn', 'content' => [
            ['type' => 'text', 'text' => 'Siparişiniz hazırlanıyor.'],
        ]]),
]);

$this->postJson(route('ai.send'), ['message' => 'ORD-1001 ne durumda?'])
     ->assertOk()
     ->assertJson(['reply' => 'Siparişiniz hazırlanıyor.']);

Http::assertSentCount(2);   // tool turu + nihai cevap""")

# ================================================================ 7. KAYNAK KODLAR
H1("7. Dosyaların Tam Kaynak Kodları")
P("Aşağıdaki kodlar proje dosyalarından **değiştirilmeden** alınmıştır. 104 karakterden uzun satırlar sayfaya "
  "sığması için bölünmüş ve devam satırları `»` ile işaretlenmiştir.")
story.append(CondPageBreak(220))
H2("7.1 AgentController.php")
full_source(C)
story.append(CondPageBreak(220))
H2("7.2 AiAgent.php")
full_source(A)
story.append(CondPageBreak(220))
H2("7.3 AiClient.php")
full_source(K)
story.append(CondPageBreak(220))
H2("7.4 ToolsService.php")
full_source(T)
story.append(CondPageBreak(220))
H2("7.5 ToolSchema.php")
full_source(S)
H2("7.6 Akışa dahil destekleyici dosyalar")
P("Kapsamdaki dosyalar bunlar olmadan anlaşılamayacağı için başvuru amacıyla eklenmiştir.")
full_source("routes/web.php")
cfg = read_src("config/services.php").split("\n")
i0 = next(i for i, l in enumerate(cfg) if "'anthropic'" in l)
story.append(file_bar("config/services.php", f"yalnızca ilgili bölüm · satır {i0 + 1}–{i0 + 4}"))
story.append(XPreformatted(code_xml("\n".join(cfg[i0:i0 + 4]), i0 + 1, True), code_style()))
full_source("app/Models/Customer.php")
full_source("app/Models/Order.php")

# ================================================================ 8. ÖZET
H1("8. Genel Mimari Özeti")
H2("8.1 Tek paragrafta sistem")
P("Kullanıcının sorusu `AgentController` üzerinden doğrulanarak `AiAgent`'a verilir. AiAgent, system prompt ve "
  "`ToolSchema`'daki tool tanımlarıyla birlikte soruyu `AiClient` aracılığıyla Anthropic Messages API'ye gönderir. "
  "Model veri isterse `stop_reason: tool_use` döner. AiAgent ilgili tool'u whitelist korumalı `ToolsService` "
  "üzerinden çalıştırır, Eloquent ile veritabanından okunan sonucu `tool_result` olarak geçmişe ekler ve modele "
  "tekrar sorar. Bu döngü model nihai cevabı üretene kadar, en fazla 5 tur sürer. Son yanıttaki metin blokları "
  "birleştirilip `{reply}` JSON'u olarak tarayıcıya döner. İş seviyesindeki olumsuzluklar modele veri olarak "
  "gider; altyapı hataları 502/500'e çevrilir.")
H2("8.2 Her dosya tek cümlede")
table([
    ["Dosya", "Rolü"],
    ["AgentController", "HTTP kapısı: doğrular, ajanı çalıştırır, hatayı/cevabı JSON'a çevirir."],
    ["AiAgent", "Orkestratör: persona + tool listesi + sınırlı tool-use döngüsü."],
    ["AiClient", "Anthropic'e tek HTTP çağrısı yapan ince adaptör."],
    ["ToolsService", "Whitelist korumalı tool uygulamaları; Eloquent ile veri okur, sade dizi döner."],
    ["ToolSchema", "Modele sunulan tool sözleşmeleri; whitelist'in tek kaynağı."],
], [110, 373])
H2("8.3 Akılda tutulacak sözleşmeler")
BL([
    "**Tool adı = ToolsService metod adı** (snake_case). Biri değişirse diğeri de değişmeli.",
    "**Tool dönüşü her zaman** `['status' => 'success'|'error', ...]` şeklindedir. `error`, modele `is_error: true` "
    "olarak gider.",
    "**Katmanlar arası veri formatı Anthropic Messages formatıdır** (`messages`, `content` blokları, `stop_reason`).",
    "**Controller ↔ frontend sözleşmesi:** başarıda `{reply: string}`, hatada `{message: string}`.",
    "**Yapılandırma:** `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` → `config('services.anthropic.*')`.",
])
H2("8.4 Yeni bir tool nasıl eklenir? (reçete)")
NL([
    "`ToolSchema::all()` dizisine yeni bir tanım ekle: `name`, ayrıntılı `description` (ne zaman kullanılır / "
    "kullanılmaz) ve `input_schema`.",
    "`ToolsService`'e **aynı isimde** public bir metod ekle: `array $input` alsın, girdiyi normalize etsin, "
    "`['status' => …]` dönsün.",
    "Gerekirse `AiAgent::$system` prompt'una yeni tool'la ilgili davranış kuralı ekle.",
    "`Http::fake` ile bir feature testi yaz (bkz. 6.6).",
])
code("""// 1) app/Schema/ToolSchema.php
[
    'name' => 'get_customer_by_email',
    'description' => 'E-posta adresiyle tek bir müşteriyi bulur. İsimle arama için get_customer_orders kullanın.',
    'input_schema' => [
        'type' => 'object',
        'properties' => ['email' => ['type' => 'string', 'description' => 'Örn: ahmet@example.com']],
        'required' => ['email'],
    ],
],

// 2) app/Services/Ai/ToolsService.php
public function get_customer_by_email(array $input): array
{
    $email = strtolower(trim((string) ($input['email'] ?? '')));
    $customer = Customer::where('email', $email)->first();

    return $customer
        ? ['status' => 'success', 'customer' => $customer->only('name', 'email', 'city')]
        : ['status' => 'error', 'message' => 'Müşteri bulunamadı.'];
}""")
H2("8.5 İyileştirme yol haritası")
table([
    ["Konu", "Öneri", "Öncelik"],
    ["Yetkilendirme", "AI route'larına `auth` (ve gerekirse rol kontrolü) ekle.", "Yüksek"],
    ["Rate limiting", "`throttle:20,1` gibi bir limit ile maliyet ve kötüye kullanım koruması.", "Yüksek"],
    ["Hata eşleme", "`ConnectionException`'ı yakalayıp 502/504 döndür.", "Orta"],
    ["Yapılandırma", "`.env.example`'a `ANTHROPIC_API_KEY` ve `ANTHROPIC_MODEL` ekle; boşsa açık hata ver.", "Orta"],
    ["Dayanıklılık", "`Http::retry()` ile 429/529 için geri çekilmeli tekrar deneme.", "Orta"],
    ["Testler", "`Http::fake` ile ajan döngüsü, whitelist ve hata dalları için feature testleri.", "Orta"],
    ["Sohbet geçmişi", "Frontend'in geçmişi göndermesi veya oturumda saklama; `messages` dizisine ekleme.", "Düşük"],
    ["Maliyet", "System prompt ve tools için prompt caching; `usage` alanını loglama.", "Düşük"],
    ["UX", "`max_tokens` kesilmesini algılayıp kullanıcıyı bilgilendirme; streaming (SSE).", "Düşük"],
    ["Doğruluk", "LIKE sorgusunda `%` ve `_` karakterlerini escape etme.", "Düşük"],
], [95, 323, 65])
H2("8.6 Altı ay sonra geri döndüğünüzde kontrol listesi")
BL([
    "İstek nereden başlıyor? → `routes/web.php` → `AgentController::post`.",
    "Model ne biliyor? → Yalnızca `AiAgent::$system` + `ToolSchema::all()` + o anki `$messages`.",
    "Veri nereden geliyor? → Yalnızca `ToolsService` metotları (Eloquent).",
    "API ile ilgili bir sorun mu var? → `storage/logs/laravel.log` içinde “Anthropic API hatası” kaydı (status + body).",
    "Model yanlış tool seçiyor mu? → Önce `ToolSchema` açıklamalarını iyileştir, kodu değil.",
    "Model veri uyduruyor mu? → System prompt kurallarını ve tool çıktısının yeterliliğini kontrol et.",
])

# ---------------------------------------------------------------- build
doc = Doc(OUT)
doc.multiBuild(story)
print("OK", OUT)
