import sqlite3

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

from mUtilities.DataBaseHandler import DataBaseHandler


def generate_pdf(tests):
    # Create a PDF document object
    pdf_file = SimpleDocTemplate("Scan Report.pdf", pagesize=A4)

    # Create a list to hold the document elements
    elements = []

    # Add the title
    title = "Scan Report"
    elements.append(Paragraph(title, getSampleStyleSheet()['Heading1']))

    # Add the current date and time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph("Date and time: " + now, getSampleStyleSheet()['Normal']))

    spacer = Spacer(1, 20)
    elements.append(spacer)

    crawled_data = get_all_data()
    crawled_data = [[x[1], x[4], x[5], x[6]] for x in crawled_data]
    if len(crawled_data) != 0:
        elements.append(Paragraph("Pages found:", getSampleStyleSheet()['Normal']))
        # Create a table with the data
        data = [['URL', 'Elapsed', 'Status', 'Reason']]
        for row in crawled_data:
            data.append(list(row))

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)

    try:
        for test in tests:
            for result in test.results:
                (time, message) = result
                date_time = datetime.fromtimestamp(int(time))
                spacer = Spacer(1, 20)
                elements.append(spacer)
                elements.append(Paragraph(str(date_time), getSampleStyleSheet()['Normal']))
                for line in message.splitlines():
                    elements.append(Paragraph(line, getSampleStyleSheet()['Normal']))
    except:
        pass

    # Build the PDF
    pdf_file.build(elements)
    print("Report Generated!")


def get_all_data():
    try:
        # Create a connection to the database
        conn = sqlite3.connect(f'urls_database.db')
        c = conn.cursor()
        # Get an array of all the URLs from the crawled_links table
        c.execute("SELECT * FROM crawled_links")
        url_array = c.fetchall()
        # Close the connection to the database
        c.close()
        conn.close()
        return url_array
    except:
        pass
    finally:
        pass

# END OF run_tests_for_links
