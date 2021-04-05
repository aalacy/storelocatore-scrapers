import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgselenium import SgChrome
from bs4 import BeautifulSoup

website = "unfi_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "authority": "www.unfi.com",
    "method": "GET",
    "path": "/locations",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "visid_incap_536781=kRXhn/08RI+24aoBO2PrKBsnGmAAAAAAQUIPAAAAAAAXVT4TPM5TbvN9NZq2aSCS; modal_shown=yes; _ga=GA1.2.599170801.1612326712; incap_ses_957_536781=BpfXGvxvizaG0Pg6qPJHDbIwHWAAAAAATgllZ2VtSVDKQe4kayxm8w==; has_js=1; merger_modal=1; _gid=GA1.2.1653675809.1612525782; incap_ses_262_536781=Pvn1LKzC9iowSSrW8s+iA0U8HWAAAAAAhZ3rC0gzPzivvsej/FiLeA==; nlbi_536781=+es8PFQsUDzuCyb24PWBEQAAAADFBYmZkoYeFRoCV7qP80vG; _gat_UA-4370112-9=1",
    "if-none-match": '"1612459826-0"',
    "referer": "https://www.unfi.com/locations",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    data = []
    with SgChrome() as driver:
        driver.get("https://www.unfi.com/locations")
        loclist = driver.page_source.split('"markers":')[1].split(',"styleBubble":', 1)[
            0
        ]
    loclist = json.loads(loclist)
    for loc in loclist:
        temp = loc["text"]
        soup = BeautifulSoup(temp, "html.parser")
        title = soup.find("strong").text
        lat = loc["latitude"]
        longt = loc["longitude"]
        street = soup.find("span", {"itemprop": "streetAddress"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text.replace(",", "")
        state = soup.find("span", {"itemprop": "addressRegion"}).text
        pcode = soup.find("span", {"class": "postal-code"}).text
        try:
            phone = soup.find("span", {"itemprop": "telephone"}).text
        except:
            phone = "<MISSING>"
        data.append(
            [
                "https://www.unfi.com/",
                "https://www.unfi.com/locations",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
