from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress
import re
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tcmarkets_com")


def get_value(item):
    if item is None or len(item) == 0:
        item = "<MISSING>"
    return item


def parse_address(address):
    address = usaddress.parse(address)

    street = ""
    city = ""
    state = ""
    zipcode = ""
    for addr in address:
        if addr[1] == "PlaceName":
            city += addr[0].replace(",", "") + " "
        elif addr[1] == "ZipCode":
            zipcode = addr[0].replace(",", "")
        elif addr[1] == "StateName":
            state = addr[0].replace(",", "")
        else:
            street += addr[0].replace(",", "") + " "
    return {
        "street": get_value(street),
        "city": get_value(city),
        "state": get_value(state),
        "zipcode": get_value(zipcode),
    }


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    # Your scraper here

    res = session.get("https://tcmarkets.com/store-finder/")
    soup = BeautifulSoup(res.text, "html.parser")
    stores = soup.find_all("a", {"itemprop": "url"})

    del stores[0]
    for store in stores:
        url = store.get("href")

        logger.info(url)
        if "https://tcmarkets.com/store-finder/dixon-ace-hardware/" in url:
            continue
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        data = soup.find("div", {"class": "fl-rich-text"}).find_all("p")

        for p in data:
            if "Store Address" in p.text:
                addr = p

        phone = ""
        if "Hours" not in addr.text:
            ad = addr
            tim = data[data.index(addr) + 1].text.strip()
            addr = addr.text.strip()
            p = re.findall(r"\([\d]{3}\)[\d \-]+", tim)
            logger.info(p)
            if p != []:
                phone = p[0]

                tim = data[data.index(ad) + 2].text.strip()
        else:

            addr = addr.text.strip()
            tim = re.findall("Store Hours:(.*)", addr, re.DOTALL)[0]

            addr = addr.replace(tim, "")

        if phone == "":
            phone = re.findall(r"\([\d]{3}\)[\d \-]+", addr)[0]

        tim = " ".join(tim.replace("Store Hours:", "").strip().split("\n"))

        addr = " ".join(
            addr.replace("Store Address", "").replace(phone, "").strip().split("\n")
        )

        parsed_address = parse_address(addr)
        city = parsed_address["city"]
        state = parsed_address["state"]
        zip = parsed_address["zipcode"]
        street = parsed_address["street"]
        if city == "<MISSING>" and state == "<MISSING>" and zip == "<MISSING>":
            for p in data:
                if "Store Address" in p.text:
                    addr = p.text + ", " + data[data.index(p) + 1].text
                    break
            addr = addr.replace(phone, "").strip()
            parsed_address = parse_address(addr)
            city = parsed_address["city"]
            state = parsed_address["state"]
            zip = parsed_address["zipcode"]

        loc = city
        if loc == "<MISSING>":
            loc = url.strip().strip("/").split("/")[-1].replace("-", " ").upper()

        yield SgRecord(
            locator_domain="https://tcmarkets.com",
            page_url=url,
            location_name=loc,
            street_address=street,
            city=city,
            state=state,
            zip_postal=zip,
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude="<MISSING>",
            longitude="<MISSING>",
            hours_of_operation=tim,
        )


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
