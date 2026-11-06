import pdfplumber


def extract_text_from_pdf(pdf_path):

    extracted_text = ""

    try:

        with pdfplumber.open(pdf_path) as pdf:

            for page_number, page in enumerate(pdf.pages, start=1):

                page_text = page.extract_text()

                if page_text:
                    extracted_text += f"\n--- Page {page_number} ---\n"
                    extracted_text += page_text + "\n"

        return extracted_text.strip()

    except Exception as error:

        raise ValueError(f"PDF extraction failed: {error}")