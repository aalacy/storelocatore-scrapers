import json
import time

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="prada.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.prada.com/us/en/store-locator.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="d-none")[-1].find_all("a")
    locator_domain = "prada.com"

    for item in items:
        link = item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        js = base.find(id="jsonldLocalBusiness").contents[0].replace("\r\n", " ")
        store = json.loads(js)

        country_code = store["address"]["addressCountry"]
        if not country_code:
            time.sleep(5)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            js = base.find(id="jsonldLocalBusiness").contents[0].replace("\r\n", " ")
            store = json.loads(js)

        country_code = store["address"]["addressCountry"]
        log.info(link)
        location_name = store["name"]
        street_address = (
            store["address"]["streetAddress"]
            .replace("Bal Harbour FL 33154", ", FL")
            .replace("W. Montreal, QC H3G 1P7", ", QC")
            .replace("New York City, New York 10022", ", New York")
            .strip()
            .replace("  ", " ")
        )
        street_address = (
            street_address.split(", Houston")[0]
            .split(", New York")[0]
            .split(", Manchester")[0]
            .strip()
        )
        city = store["address"]["addressLocality"]
        state = ""
        zip_code = store["address"]["postalCode"]
        if not zip_code:
            zip_code = "<MISSING>"

        if country_code == "US" or country_code == "CA":
            street_address = street_address.replace("Honolulu, HI 96819", "HI")
            state = street_address.split(",")[-1].strip()
            street_address = ",".join(street_address.split(",")[:-1])

        store_number = link.split(".")[-2]
        location_type = "<MISSING>"
        phone = store["telephone"]
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = (
            store["openingHours"].strip().replace("  ", " ").replace("--", "Closed")
        )
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        try:
            if "Temporarily" in item.find(class_="singleStore__temporaryClosed").text:
                hours_of_operation = item.find(
                    class_="singleStore__temporaryClosed"
                ).text
        except:
            pass

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
