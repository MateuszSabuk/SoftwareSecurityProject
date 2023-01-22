from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet

data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]


def create_pdf():
    story = []

    # Initialise the simple document template
    doc = SimpleDocTemplate(f"blog.pdf",
                            page_size=letter,
                            bottomMargin=.4 * inch,
                            topMargin=.4 * inch,
                            rightMargin=.8 * inch,
                            leftMargin=.8 * inch)

    # set the font style
    styles = getSampleStyleSheet()
    styleN = styles['Normal']

    for count, d in enumerate(data, 1):
        p_count = Paragraph(f" Data: {count} ")
        story.append(Spacer(1, 12))
        story.append(p_count)
        for k, v in d.items():
            # extract and add key value pairs to PDF
            p = Paragraph(k + " : " + str(v), styleN)
            story.append(p)
            story.append(Spacer(1, 2))
    # build PDF using the data
    doc.build(story)

