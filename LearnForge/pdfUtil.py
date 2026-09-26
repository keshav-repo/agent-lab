from pathlib import Path

from fpdf import FPDF
from fpdf.fonts import FontFace

from models import LearningEntityWithAliases


# ============================================================================
# Configuration
# ============================================================================

_FONT_CANDIDATES = (
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
)

DEFAULT_COLUMNS = [
    "ID",
    "Text",
    "Category",
    "Subcategory",
    "Aliases",
]

ALL_COLUMNS = (
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


# ============================================================================
# Column Configuration
# ============================================================================
#
# weight:
#   Relative importance of the column when distributing available width.
#
# min:
#   Minimum width in mm.
#
# max:
#   Maximum width in mm.
#
# Text and Aliases intentionally have larger weights and maximum widths.
# Category and Subcategory intentionally have smaller limits.
#

COLUMN_CONFIG = {
    "ID": {
        "weight": 0.5,
        "min": 10,
        "max": 15,
    },
    "Text": {
        "weight": 3.0,
        "min": 35,
        "max": 95,
    },
    "Category": {
        "weight": 1.0,
        "min": 20,
        "max": 35,
    },
    "Subcategory": {
        "weight": 1.0,
        "min": 20,
        "max": 40,
    },
    "Topic": {
        "weight": 1.5,
        "min": 25,
        "max": 50,
    },
    "Subtopic": {
        "weight": 1.5,
        "min": 25,
        "max": 50,
    },
    "Concept": {
        "weight": 1.5,
        "min": 25,
        "max": 50,
    },
    "Tags": {
        "weight": 1.2,
        "min": 20,
        "max": 45,
    },
    "Aliases": {
        "weight": 3.0,
        "min": 35,
        "max": 95,
    },
}


# ============================================================================
# Value Formatting
# ============================================================================

def _cell(value) -> str:
    """
    Convert a value into a printable string.
    """
    if value is None:
        return ""

    return str(value).strip()


def _one_line(value) -> str:
    """
    Keep metadata values on one line where possible.

    Non-breaking spaces prevent FPDF from wrapping individual words.
    """
    return _cell(value).replace(" ", "\u00a0")


def _tags_cell(tags: list[str]) -> str:
    """
    Convert tags into a comma-separated string.
    """
    return _one_line(
        ", ".join(
            tag.strip()
            for tag in tags
            if tag and tag.strip()
        )
    )


def _aliases_cell(aliases: list[str]) -> str:
    """
    Convert aliases into a bullet list.
    """
    return "\n".join(
        f"• {alias.strip()}"
        for alias in aliases
        if alias and alias.strip()
    )


# ============================================================================
# Entity -> Column Values
# ============================================================================

def _get_column_values(
    entity: LearningEntityWithAliases,
) -> dict[str, str]:
    """
    Convert an entity into printable column values.
    """
    return {
        "ID": _one_line(entity.id),
        "Text": _cell(entity.text) or "(untitled)",
        "Category": _one_line(entity.category),
        "Subcategory": _one_line(entity.subcategory),
        "Topic": _one_line(entity.topic),
        "Subtopic": _one_line(entity.subtopic),
        "Concept": _one_line(entity.concept),
        "Tags": _tags_cell(entity.tags),
        "Aliases": _aliases_cell(entity.aliases),
    }


# ============================================================================
# Column Handling
# ============================================================================

def _normalize_columns(
    column_to_print: list[str],
) -> list[str]:
    """
    Keep only supported columns.

    Invalid columns are silently ignored.

    If every supplied column is invalid, return the default columns.
    """
    valid_columns = [
        column
        for column in column_to_print
        if column in ALL_COLUMNS
    ]

    if not valid_columns:
        return DEFAULT_COLUMNS.copy()

    return valid_columns


# ============================================================================
# Font Handling
# ============================================================================

def _find_unicode_font() -> str | None:
    """
    Find the first available Unicode-compatible font.
    """
    for path in _FONT_CANDIDATES:
        if Path(path).is_file():
            return path

    return None


def _configure_font(pdf: FPDF) -> str:
    """
    Configure a Unicode-compatible font.

    Falls back to Helvetica if no Unicode font is available.
    """
    font_path = _find_unicode_font()

    if not font_path:
        return "Helvetica"

    pdf.add_font(
        "Body",
        "",
        font_path,
    )

    pdf.add_font(
        "Body",
        "B",
        font_path,
    )

    return "Body"


# ============================================================================
# PDF Class
# ============================================================================

class _EntityPdf(FPDF):

    def __init__(
        self,
        font_family: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.font_family = font_family

    def header(self):
        """
        Render PDF header.
        """
        self.set_font(
            self.font_family,
            "B",
            14,
        )

        self.cell(
            0,
            10,
            "Learning Entities",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        self.ln(1)

    def footer(self):
        """
        Render PDF footer.
        """
        self.set_y(-12)

        self.set_font(
            self.font_family,
            size=9,
        )

        self.set_text_color(
            100,
            100,
            100,
        )

        self.cell(
            0,
            8,
            f"Page {self.page_no()}/{{nb}}",
            align="C",
        )

        self.set_text_color(
            0,
            0,
            0,
        )


# ============================================================================
# Dynamic Column Width
# ============================================================================

def _calculate_content_score(
    entities: list[LearningEntityWithAliases],
    column: str,
) -> float:
    """
    Calculate a rough content-length score for a column.

    This is intentionally capped so a single extremely long value
    doesn't consume the entire page.
    """
    if not entities:
        return 0.0

    max_length = 0
    total_length = 0
    count = 0

    for entity in entities:
        values = _get_column_values(entity)
        value = values.get(column, "")

        # Convert newlines to spaces for measuring.
        value = value.replace("\n", " ")

        length = len(value)

        max_length = max(
            max_length,
            length,
        )

        total_length += length
        count += 1

    if count == 0:
        return 0.0

    average_length = total_length / count

    # Combine average and maximum.
    #
    # Average gets more importance because it represents the
    # general content of the column.
    score = (
        average_length * 0.7
        + min(max_length, 120) * 0.3
    )

    return score


def _calculate_column_widths(
    entities: list[LearningEntityWithAliases],
    columns: list[str],
    available_width: float,
) -> list[float]:
    """
    Calculate dynamic column widths.

    The algorithm:
        1. Start with minimum widths.
        2. Calculate content scores.
        3. Give larger columns more space based on weight/content.
        4. Respect maximum widths.
        5. Normalize everything to fit the page.
    """

    if not columns:
        return []

    # ------------------------------------------------------------------------
    # Step 1: Minimum widths
    # ------------------------------------------------------------------------

    widths = {
        column: COLUMN_CONFIG[column]["min"]
        for column in columns
    }

    # ------------------------------------------------------------------------
    # Step 2: Calculate remaining width
    # ------------------------------------------------------------------------

    minimum_total = sum(widths.values())

    if minimum_total >= available_width:
        return _fit_widths_to_page(
            widths,
            available_width,
        )

    remaining_width = available_width - minimum_total

    # ------------------------------------------------------------------------
    # Step 3: Calculate priority score
    # ------------------------------------------------------------------------

    scores = {}

    for column in columns:
        config = COLUMN_CONFIG[column]

        content_score = _calculate_content_score(
            entities,
            column,
        )

        # Base weight ensures important columns such as Text and
        # Aliases remain large even when their content is short.
        content_factor = 1.0

        if content_score > 0:
            content_factor += min(
                content_score / 80.0,
                1.5,
            )

        scores[column] = (
            config["weight"]
            * content_factor
        )

    # ------------------------------------------------------------------------
    # Step 4: Distribute remaining width
    # ------------------------------------------------------------------------

    active_columns = set(columns)

    while remaining_width > 0.1 and active_columns:

        total_score = sum(
            scores[column]
            for column in active_columns
        )

        if total_score <= 0:
            break

        distributed = 0.0
        columns_to_remove = set()

        for column in active_columns:

            config = COLUMN_CONFIG[column]

            share = (
                remaining_width
                * scores[column]
                / total_score
            )

            current_width = widths[column]

            max_width = config["max"]

            available_for_column = (
                max_width - current_width
            )

            allocation = min(
                share,
                available_for_column,
            )

            widths[column] += allocation
            distributed += allocation

            if widths[column] >= max_width - 0.01:
                columns_to_remove.add(column)

        if distributed <= 0.01:
            break

        remaining_width -= distributed

        active_columns -= columns_to_remove

    # ------------------------------------------------------------------------
    # Step 5: Make sure total fits exactly
    # ------------------------------------------------------------------------

    return _fit_widths_to_page(
        widths,
        available_width,
    )


def _fit_widths_to_page(
    widths: dict[str, float],
    available_width: float,
) -> list[float]:
    """
    Normalize widths so the final total fits exactly within the page.
    """
    total_width = sum(widths.values())

    if total_width <= 0:
        return []

    # If the widths are smaller than the available area,
    # distribute the remaining space proportionally.
    if total_width < available_width:
        factor = available_width / total_width

        return [
            round(width * factor, 2)
            for width in widths.values()
        ]

    # If widths are larger, scale them down.
    factor = available_width / total_width

    return [
        round(width * factor, 2)
        for width in widths.values()
    ]


# ============================================================================
# PDF Setup
# ============================================================================

def _create_pdf() -> tuple[FPDF, str]:
    """
    Create and configure the PDF instance.
    """
    pdf = _EntityPdf(
        font_family="Helvetica",
        orientation="L",
        format="A4",
    )

    pdf.alias_nb_pages()

    pdf.set_auto_page_break(
        auto=True,
        margin=14,
    )

    pdf.set_margins(
        left=12,
        top=12,
        right=12,
    )

    font_family = _configure_font(pdf)

    pdf.font_family = font_family

    return pdf, font_family


def _available_page_width(pdf: FPDF) -> float:
    """
    Return the available horizontal page width.
    """
    return (
        pdf.w
        - pdf.l_margin
        - pdf.r_margin
    )


# ============================================================================
# Table
# ============================================================================

def _create_heading_style() -> FontFace:
    """
    Create table heading style.
    """
    return FontFace(
        emphasis="BOLD",
        fill_color=(230, 230, 230),
    )


def _create_table(
    pdf: FPDF,
    entities: list[LearningEntityWithAliases],
    columns: list[str],
):
    """
    Create a table with dynamically calculated column widths.
    """
    available_width = _available_page_width(pdf)

    column_widths = _calculate_column_widths(
        entities=entities,
        columns=columns,
        available_width=available_width,
    )

    return pdf.table(
        col_widths=column_widths,
        text_align="LEFT",
        v_align="TOP",
        line_height=4,
        headings_style=_create_heading_style(),
        repeat_headings=1,
        padding=(
            0.6,
            1.2,
            0.6,
            1.2,
        ),
    )


# ============================================================================
# Table Rows
# ============================================================================

def _write_table_header(
    table,
    columns: list[str],
) -> None:
    """
    Write table header.
    """
    header = table.row()

    for column in columns:
        header.cell(column)


def _write_entity_row(
    table,
    entity: LearningEntityWithAliases,
    columns: list[str],
) -> None:
    """
    Write one entity row.
    """
    values = _get_column_values(entity)

    row = table.row()

    for column in columns:
        row.cell(
            values.get(column, "")
        )


def _write_empty_row(
    table,
    columns: list[str],
) -> None:
    """
    Write empty table message.
    """
    row = table.row()

    row.cell(
        "No entities selected.",
        colspan=len(columns),
    )


# ============================================================================
# Public API
# ============================================================================

def convert_to_pdf(
    entities: list[LearningEntityWithAliases],
    output_path: str = "output.pdf",
    column_to_print: list[str] | None = None,
) -> str:
    """
    Convert learning entities to a PDF table.

    Args:
        entities:
            List of learning entities.

        output_path:
            Destination PDF path.

        column_to_print:
            Columns to include in the PDF.

            Defaults to:

                [
                    "ID",
                    "Text",
                    "Category",
                    "Subcategory",
                    "Aliases",
                ]

            Invalid column names are ignored.

            If all supplied columns are invalid,
            default columns are used.

    Returns:
        Path of the generated PDF.
    """

    # ------------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------------

    if column_to_print is None:
        columns = DEFAULT_COLUMNS.copy()
    else:
        columns = _normalize_columns(
            column_to_print
        )

    # ------------------------------------------------------------------------
    # PDF
    # ------------------------------------------------------------------------

    pdf, font_family = _create_pdf()

    pdf.add_page()

    # ------------------------------------------------------------------------
    # Item count
    # ------------------------------------------------------------------------

    pdf.set_font(
        font_family,
        size=7,
    )

    pdf.cell(
        0,
        5,
        f"{len(entities)} item(s)",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(2)

    # ------------------------------------------------------------------------
    # Table
    # ------------------------------------------------------------------------

    with _create_table(
        pdf=pdf,
        entities=entities,
        columns=columns,
    ) as table:

        _write_table_header(
            table,
            columns,
        )

        if not entities:
            _write_empty_row(
                table,
                columns,
            )
        else:
            for entity in entities:
                _write_entity_row(
                    table,
                    entity,
                    columns,
                )

    # ------------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------------

    destination = Path(output_path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pdf.output(
        str(destination)
    )

    return str(destination)