from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import base64

chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Use the updated headless mode syntax
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-allow-origins=*")  # Required for Chrome 124+ :cite[4]

# Disable Chrome's PDF Viewer to force download behavior (optional for CDP method)
chrome_options.add_experimental_option('prefs', {
    "plugins.always_open_pdf_externally": True,
    "download.prompt_for_download": False
})

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.uptodate.com/contents/seasonal-influenza-in-adults-clinical-manifestations-and-diagnosis")  # Replace with your target URL

time.sleep(5)

# Configure PDF printing parameters :cite[4]:cite[5]
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
with open("output.pdf", "wb") as f:
    f.write(pdf_data)

driver.quit()
