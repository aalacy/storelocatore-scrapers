from lxml import html
import time
import csv

from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "arco.co.uk"
website = "https://www.arco.co.uk"
MISSING = "<MISSING>"


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetchStores():
    response = request_with_retries(f"{website}/branchloc")
    body = html.fromstring(response.text, "lxml")
    datas = body.xpath('//ol[contains(@id, "mapLocations")]/li')
    stores = []
    store = {}
    for data in datas:
        ul = data.xpath(".//ul")
        if len(ul) == 0:
            store["location_name"] = data.xpath(".//text()")[0]
        else:
            ul = ul[0]
            store["page_url"] = ul.xpath('.//a[text()="View details"]/@href')[0].split(
                "?"
            )[0]
            store["addr"] = ul.xpath('.//li[@class="addr"]/text()')[0]
            store["latitude"] = ul.xpath('.//li[@class="lat"]/text()')[0]
            store["longitude"] = ul.xpath('.//li[@class="lng"]/text()')[0]
            stores.append(store)
            store = {}
    return stores


def getHoo(texts):
    for text in texts:
        if "day" in text:
            text = text.replace("\r", " ").replace("\n", " ").replace("\xa0", " ")
            text = " ".join(text.split())
            return text
    return MISSING


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    newStores = []
    count = 0
    for store in stores:
        count = count + 1
        location_name = store["location_name"]
        page_url = store["page_url"]
        latitude = store["latitude"].replace("\r", "").replace("\n", "")
        longitude = store["longitude"].replace("\r", "").replace("\n", "")
        log.debug(f"{count}. crawling {page_url} ...")
        response = request_with_retries(page_url)
        body = html.fromstring(response.text, "lxml")
        table = body.xpath('//table[@id="addresstb"]/tr')
        trTexts = {}
        for tr in table:
            title = tr.xpath(".//td/strong/text()")
            value = tr.xpath(".//td/text()")
            if len(title) > 0 and len(value) > 0:
                value = " ".join(value).replace("\r", " ").replace("\n", " ")
                value = " ".join(value.split())
                trTexts[title[0]] = value

        store_number = page_url.split("/")[len(page_url.split("/")) - 1]
        location_type = trTexts["Address:"] if "Address:" in trTexts else MISSING
        street_address = trTexts["Address:"] if "Address:" in trTexts else MISSING
        city = trTexts["City:"] if "City:" in trTexts else MISSING
        zip_postal = trTexts["Postcode:"] if "Postcode:" in trTexts else MISSING
        state = MISSING
        country_code = "UK"
        phone = trTexts["Telephone:"] if "Telephone:" in trTexts else MISSING
        hours_of_operation = getHoo(body.xpath('//p[@class="openingtimes"]/text()'))
        raw_address = f"{street_address}, {city}, {zip_postal}"

        newStores.append(
            {
                "locator_domain": DOMAIN,
                "store_number": store_number,
                "page_url": page_url,
                "location_name": location_name,
                "location_type": location_type,
                "street_address": street_address,
                "city": city,
                "zip_postal": zip_postal,
                "state": state,
                "country_code": country_code,
                "phone": phone,
                "latitude": latitude,
                "longitude": longitude,
                "hours_of_operation": hours_of_operation,
                "raw_address": raw_address,
                "Arco Store": "Yes" if "Arco Store" in location_name else "No",
            }
        )

    log.info(f"Total scrapped {count}")
    return newStores


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        headers = [
            "locator_domain",
            "page_url",
            "location_name",
            "street_address",
            "city",
            "state",
            "zip_postal",
            "country_code",
            "store_number",
            "phone",
            "location_type",
            "latitude",
            "longitude",
            "raw_address",
            "hours_of_operation",
            "Arco Store",
        ]
        writer.writerow(headers)

        for row in data:
            d = []
            for header in headers:
                d.append(row[header])
            writer.writerow(d)


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    result = fetchData()
    write_output(result)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
