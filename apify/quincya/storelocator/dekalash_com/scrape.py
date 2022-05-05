from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger(logger_name="dekalash.com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    api_link = "https://api.storepoint.co/v1/15e2b4dd23ff14/locations?lat=39.011902&long=-98.4842465&radius=5000"

    store_data = session.get(api_link, headers=headers).json()["results"]["locations"]

    locator_domain = "dekalash.com"

    for store in store_data:
        store_number = store["id"]
        link = store["website"]
        location_name = store["name"]
        raw_address = store["streetaddress"].split(",")[:-1]
        street_address = " ".join(raw_address[:-2]).strip().replace("  ", " ")
        city = raw_address[-2].strip()
        state = raw_address[-1].split()[0].strip()
        zip_code = raw_address[-1].split()[1].strip()
        country_code = store["streetaddress"].split(",")[-1].strip()
        location_type = "<MISSING>"

        if "4346 Belden Village" in street_address:
            zip_code = "44718"

        phone = store["phone"]
        if not phone:
            phone = "<MISSING>"

        latitude = store["loc_lat"]
        longitude = store["loc_long"]

        log.info(link)
        req = session.get(link, headers=headers)

        if req.status_code == 404:
            link = "https://dekalash.com/find-a-studio/"
            hours_of_operation = ""
        else:
            link = req.url
            base = BeautifulSoup(req.text, "lxml")

            try:
                if "coming soon" in base.find(class_="elementor-row").text.lower():
                    continue
            except:
                continue

            if "temporarily closed" in base.find(class_="elementor-row").text.lower():
                hours_of_operation = "Temporarily Closed"
            else:
                hours_of_operation = " ".join(
                    list(base.find(class_="IiXf4c").stripped_strings)
                )

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
