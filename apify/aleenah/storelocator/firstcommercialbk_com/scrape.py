from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import usaddress
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("firstcommercialbk_com")


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    # Your scraper here
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    }
    res = session.get("https://www.firstcommercialbk.com/locations/", headers=headers)

    soup = BeautifulSoup(res.text, "html.parser")
    div = soup.find("div", {"id": "pl-30"})
    locs = div.text.split(" Address:")

    for loc in locs:
        if " Office:" in loc:
            appended = loc.split(" Office:")[-1]
            locs.insert(locs.index(loc) + 1, appended)
        if locs.index(loc) == 0:
            continue
        prev = locs[locs.index(loc) - 1]
        if "Division" in prev:
            name = prev.split("Division")[-1].split(":")[0]
        else:
            name = prev.split("p.m.")[-1]
        cur = loc.split("p.m.")[-1]
        loc = loc.replace("p.m." + cur, "p.m.")

        addr = loc.split("Phone:")[0].strip()
        if "Ridgeland" in loc:
            addr = addr.replace("Ridgeland", " Ridgeland").replace(
                "1076 Highland Colony Parkway", ""
            )
        addr = usaddress.tag(addr)[0]
        street = addr["AddressNumber"] + " " + addr["StreetName"]
        if "StreetNamePostType" in addr:
            street += " " + addr["StreetNamePostType"]
        if "SubaddressType" in addr:
            street += ", " + addr["SubaddressType"]
        if "SubaddressIdentifier" in addr:
            street += " " + addr["SubaddressIdentifier"]
        if "OccupancyType" in addr:
            street += ", " + addr["OccupancyType"]
        if "OccupancyIdentifier" in addr:
            street += " " + addr["OccupancyIdentifier"]

        if "Ridgeland" in loc:
            street += ", 1076 Highland Colony Parkway"

        city = addr["PlaceName"]
        state = addr["StateName"]
        zip = addr["ZipCode"]

        phone = re.findall(r"Phone: ([\d\-]+)", loc)[0]
        tim = re.findall(r"(.*p.m.)", loc.split("Business Hours ")[1])[0]

        yield SgRecord(
            locator_domain="https://www.firstcommercialbk.com",
            page_url="https://www.firstcommercialbk.com/locations/",
            location_name=name,
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
            hours_of_operation=tim.strip(),
        )


def scrape():
    write_output(fetch_data())


scrape()
