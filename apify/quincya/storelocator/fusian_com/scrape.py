import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("fusian_com")


def fetch_data(sgw: SgWriter):
    base_link = "https://www.fusian.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="intrinsic")
    locator_domain = "fusian.com"

    for item in items:
        link = item.a["href"]
        if "http" not in link:
            link = "https://www.fusian.com" + link
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text[1:-1].title()

        fin_script = ""
        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "latitude" in str(script):
                fin_script = str(script)
                break

        try:
            store_data = json.loads(fin_script.split(">")[1].split("<")[0])
            street_address = store_data["address"]["streetAddress"]
            city = store_data["address"]["addressLocality"]
            state = store_data["address"]["addressRegion"]
            zip_code = store_data["address"]["postalCode"]
            phone = store_data["telephone"]
            latitude = store_data["geo"]["latitude"]
            longitude = store_data["geo"]["longitude"]
        except:
            pass

        if (
            "855 W" in street_address and location_name != "Grandview"
        ) or not fin_script:
            raw_address = base.find(class_="sqs-block map-block sqs-block-map")
            store_data = json.loads(raw_address["data-block-json"])["location"]
            street_address = store_data["addressLine1"]
            city = store_data["addressLine2"].split(",")[0].strip()
            state = store_data["addressLine2"].split(",")[1].strip()
            zip_code = store_data["addressLine2"].split(",")[2].strip()

            phone = ""
            for num in range(5):
                if "Phone" in base.find_all(class_="sqs-block-content")[num].text:
                    phone = list(
                        base.find_all(class_="sqs-block-content")[num].stripped_strings
                    )[-1]
                    break

            latitude = store_data["mapLat"]
            longitude = store_data["mapLng"]

        country_code = "US"
        store_number = "<MISSING>"

        hours_of_operation = (
            base.find(string="Hours").find_next("p").get_text(" ").strip()
        )
        if ":" not in hours_of_operation:
            hours_of_operation = base.find(string="Hours:").find_next("p").text.strip()

        location_type = "<MISSING>"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
