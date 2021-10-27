from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

logger = SgLogSetup().get_logger("mavistire_com")


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    # Your scraper here

    res = session.get("https://www.mavistire.com/locations/")
    soup = BeautifulSoup(res.text, "html.parser")
    urls = soup.find_all("tr", {"class": "store-listing-row"})
    logger.info(len(urls))
    unique = set([])
    urls = list(set(urls))
    for url in urls:
        ua = url.find("a").get("href")

        url = "https://www.mavistire.com/locations/" + ua
        logger.info(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        jsonValue = re.findall(r"DrawMap\(([^\]]*\])", str(soup))[0]

        js_list = json.loads(
            jsonValue.replace("'", '"')
            .replace(':"', '":"')
            .replace('",', '","')
            .replace("{", '{"')
            .replace(',"{', ",{")
            .replace(",Lng:", '","Lng":"')
            .replace('"Lat:', '"Lat":"')
            .replace(",fillcolor", '","fillcolor')
        )

        for js in js_list:

            loc = js["Store_Name"]
            id = js["Store"]
            tim = js["Store_Hours"].replace("<br>", " ")
            street = js["Addr"]
            state = js["State"]
            city = js["City_State"].replace(state, "").strip()
            zip = js["Zip"]
            phone = js["Callcenter_Phone"]
            lat = js["Lat"]
            long = js["Lng"]
            if loc + street + id + state + city not in unique:
                unique.add(loc + street + id + state + city)
            else:
                continue

            yield SgRecord(
                locator_domain="https://www.mavistire.com/",
                page_url=url,
                location_name=loc,
                street_address=street,
                city=city,
                state=state,
                zip_postal=zip,
                country_code="US",
                store_number=id,
                phone=phone,
                location_type="<MISSING>",
                latitude=lat,
                longitude=long,
                hours_of_operation=tim.strip(),
            )


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
