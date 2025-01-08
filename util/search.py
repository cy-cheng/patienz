import requests
from googlesearch import search
import pdfkit

def search_and_export_to_pdf(query, output_pdf):
    """
    Takes a search query, finds the first website, and exports it as a PDF.

    :param query: The search query string.
    :param output_pdf: The name of the output PDF file.
    """
    try:
        # Step 1: Search for the query and get the first result
        print(f"Searching for: {query}")
        search_results = list(search(query, num_results=1))

        if not search_results:
            print("No results found.")
            return

        first_url = search_results[0]
        print(f"First URL found: {first_url}")

        # Step 2: Check if the URL is accessible
        response = requests.get(first_url)
        if response.status_code != 200:
            print(f"Failed to access the URL. Status code: {response.status_code}")
            return

        # Step 3: Convert the webpage to PDF
        print(f"Exporting {first_url} to {output_pdf}...")
        pdfkit.from_url(first_url, output_pdf)
        print(f"PDF saved as {output_pdf}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage (if running this file directly):
if __name__ == "__main__":
    query = "Python programming language"
    output_pdf = "output.pdf"
    search_and_export_to_pdf(query, output_pdf)

