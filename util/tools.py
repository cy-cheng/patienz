import shutil
import os
import requests
import concurrent.futures
import pdfkit
from googlesearch import search 


def getPDF(query, output_pdf):
    """
    Takes a search query, finds the first website, and exports it as a PDF.

    :param query: The search query string.
    :param output_pdf: The name of the output PDF file.
    """

    if os.path.exists(output_pdf):
        print(f"File already exists: {output_pdf}")
        os.remove(output_pdf)
        print(f"Deleted {output_pdf}")

    try:
        print(f"Searching for: {query}")
        search_results = list(search(query, num_results=5))
        print(f"Found {len(search_results)} search results")

        for url in search_results:
            try:
                response = requests.get(url, timeout=5)

                if response.status_code != 200:
                    print(f"Failed to access URL: {url}")
                    continue

                print(f"Exporting {url} to {output_pdf}...")
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(pdfkit.from_url, url, output_pdf)
                    try:
                        future.result(timeout=20)
                        print(f"PDF saved as {output_pdf}")
                        break
                    except concurrent.futures.TimeoutError:
                        print(f"Timeout occurred during PDF generation for URL: {url}")
                        continue
                    except Exception as e:
                        print(f"An error occurred during PDF generation: {e}")
                        continue
            except requests.exceptions.Timeout:
                print(f"Timeout occurred for URL: {url}")
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Check if the output PDF was created, if not, copy the error PDF
    if not os.path.exists(output_pdf):
        print(f"No PDF generated, copying error PDF to {output_pdf}")
        shutil.copy("tmp/error.pdf", output_pdf)


def record(file, text):
    """
    Records the text to a file.

    :param file: The file to write to.
    :param text: The text to write.
    """
    with open(file, "a") as f:
        f.write(text + "\n")

    print(f"Recorded: {text}")

# Example usage (if running this file directly):
if __name__ == "__main__":
    query = "Python programming language"
    output_pdf = "output.pdf"
    getPDF(query, output_pdf)
