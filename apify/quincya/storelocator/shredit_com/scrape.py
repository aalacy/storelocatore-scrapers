from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    api_link = "https://www.shredit.com/content/shred-it/us/en/service-locations/jcr:content/root/container/pagesection/servicelocationfinde.locations.json"
    stores = session.get(api_link, headers=headers).json()

    locator_domain = "https://www.shredit.com"

    got_phone = False
    for store in stores:
        location_name = store["title"]
        try:
            street_address = (store["address1"] + " " + store["address2"]).strip()
        except:
            street_address = store["address1"]
        if not street_address:
            continue
        city = store["city"]
        state = store["state"]
        zip_code = store["zipCode"]
        if zip_code:
            if len(zip_code) == 4:
                zip_code = "0" + zip_code
        country_code = store["country"]
        store_number = ""
        latitude = store["latitude"]
        longitude = store["longitude"]
        if latitude == "0.0":
            latitude = ""
            longitude = ""
        hours_of_operation = (
            store["openingHours"]
            .replace("\n", " ")
            .replace("<br>", "")
            .split("Witness")[0]
            .split("Haunted")[0]
            .strip()
        )
        if "per additional bag" in hours_of_operation:
            hours_of_operation = ""
        location_type = ""

        link = locator_domain + store["url"]

        if not got_phone:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            phone = base.find(string=" - Customer Service").find_previous().text.strip()
            got_phone = True

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
