from fpdf import FPDF


def wrap_text_to_lines(pdf, text, max_width):
    """Manually build lines that are guaranteed to fit within max_width"""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        # If a single word is too wide on its own, force-break it character by character
        while pdf.get_string_width(word) > max_width:
            cut = len(word)
            while cut > 0 and pdf.get_string_width(word[:cut]) > max_width:
                cut -= 1
            if cut == 0:
                cut = 1  # safety net, always progress
            lines.append(word[:cut])
            word = word[cut:]

        # Try adding word to current line
        test_line = (current_line + " " + word).strip()
        if pdf.get_string_width(test_line) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def generate_pdf_report(result, job_description):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "AI Resume Analysis Report", ln=True, align="C")
    pdf.ln(5)

    # Match Score
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, f"Match Score: {result['match_score']}%", ln=True)
    pdf.ln(3)

    max_width = pdf.w - pdf.l_margin - pdf.r_margin

    def add_section(title, items):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Helvetica", "", 11)

        if items:
            for item in items:
                clean_item = item.encode('latin-1', 'replace').decode('latin-1')
                text = f"- {clean_item}"
                lines = wrap_text_to_lines(pdf, text, max_width)
                for line in lines:
                    pdf.cell(0, 8, line, ln=True)
        else:
            pdf.cell(0, 8, "None", ln=True)
        pdf.ln(3)

    add_section("Missing Keywords:", result["missing_keywords"])
    add_section("Strengths:", result["strengths"])
    add_section("Weaknesses:", result["weaknesses"])
    add_section("Suggestions:", result["suggestions"])

    return bytes(pdf.output())