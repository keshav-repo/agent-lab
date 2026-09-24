from pathlib import Path

from fpdf import FPDF
from fpdf.fonts import FontFace

from models import LearningEntityWithAliases

_FONT_CANDIDATES = (
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
)

_COLUMNS = (
    "ID",
    "Text",
    "Category",
    "Subcategory",
    "Topic",
    "Subtopic",
    "Concept",
    "Tags",
    "Aliases",
)
# Fractions of page width. Keep metadata columns wide enough for multi-word values.
_COL_WIDTHS = (8, 42, 30, 32, 30, 30, 30, 24, 38)


def _unicode_font() -> str | None:
    for path in _FONT_CANDIDATES:
        if Path(path).is_file():
            return path
    return None


def _cell(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _one_line(value) -> str:
    """Keep metadata on one line so wrapped words are not mistaken for a list."""
    return _cell(value).replace(" ", "\u00a0")


def _tags_cell(tags: list[str]) -> str:
    return _one_line(", ".join(tag.strip() for tag in tags if tag and tag.strip()))


def _aliases_cell(aliases: list[str]) -> str:
    items = [alias.strip() for alias in aliases if alias and alias.strip()]
    return "\n".join(f"• {item}" for item in items)


class _EntityPdf(FPDF):
    def header(self):
        self.set_font(self.font_family, "B", 14)
        self.cell(0, 10, "Learning Entities", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def footer(self):
        self.set_y(-12)
        self.set_font(self.font_family, size=9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", align="C")
        self.set_text_color(0, 0, 0)


def convert_to_pdf(
    entities: list[LearningEntityWithAliases],
    output_path: str = "output.pdf",
) -> str:
    pdf = _EntityPdf(orientation="L", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(12, 12, 12)

    font_path = _unicode_font()
    if font_path:
        pdf.add_font("Body", "", font_path)
        pdf.add_font("Body", "B", font_path)
        family = "Body"
    else:
        family = "Helvetica"
    pdf.font_family = family

    pdf.add_page()
    pdf.set_font(family, size=7)
    pdf.cell(0, 5, f"{len(entities)} item(s)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    heading = FontFace(emphasis="BOLD", fill_color=(230, 230, 230))
    with pdf.table(
        col_widths=_COL_WIDTHS,
        text_align="LEFT",
        v_align="TOP",
        line_height=4,
        headings_style=heading,
        repeat_headings=1,
        padding=(0.6, 1.2, 0.6, 1.2),
    ) as table:
        header = table.row()
        for title in _COLUMNS:
            header.cell(title)

        if not entities:
            empty = table.row()
            empty.cell("No entities selected.", colspan=len(_COLUMNS))
        else:
            for entity in entities:
                row = table.row()
                row.cell(_one_line(entity.id))
                row.cell(_cell(entity.text) or "(untitled)")
                row.cell(_one_line(entity.category))
                row.cell(_one_line(entity.subcategory))
                row.cell(_one_line(entity.topic))
                row.cell(_one_line(entity.subtopic))
                row.cell(_one_line(entity.concept))
                row.cell(_tags_cell(entity.tags))
                row.cell(_aliases_cell(entity.aliases))

    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(dest))
    return str(dest)
