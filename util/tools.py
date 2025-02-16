import shutil
import os
import requests
import concurrent.futures
import pdfkit
from googlesearch import search 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager
import time
import base64

def getPDF(query, output_pdf):
    """
    Takes a search query, finds the first website, and exports it as a PDF.

    :param query: The search query string.
    :param output_pdf: The name of the output PDF file.
    """

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use the updated headless mode syntax
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-allow-origins=*")  # Required for Chrome 124+

# Disable Chrome's PDF Viewer to force download behavior (optional for CDP method)
    chrome_options.add_experimental_option('prefs', {
        "plugins.always_open_pdf_externally": True,
        "download.prompt_for_download": False
    })

    driver = webdriver.Chrome(options=chrome_options) #, service=Service(ChromeDriverManager().install()))

    if os.path.exists(output_pdf):
        print(f"File already exists: {output_pdf}")
        os.remove(output_pdf)
        print(f"Deleted {output_pdf}")

    try:
        print(f"Searching for: {query}")
        search_results = list(search(query, num_results=1))
        print(f"Found {len(search_results)} search results")

        driver.get(search_results[0])
        time.sleep(5)

        # Configure PDF printing parameters
        print_options = {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True,
            "margin": {"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"}
        }

        # Execute CDP command to generate PDF
        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)

        # Decode and save the PDF
        pdf_data = base64.b64decode(result['data'])
        with open(output_pdf, "wb") as f:
            f.write(pdf_data)

        driver.quit()

    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Check if the output PDF was created, if not, copy the error PDF
    if not os.path.exists(output_pdf):
        print(f"No PDF generated, copying error PDF to {output_pdf}")
        shutil.copy("tmp/error.pdf", output_pdf)


def getPDF2(query, output_pdf):
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
    query = "Uptodate diabetes"
    output = "output"
    getPDF(query, output)
