import re
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.club4fitness.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["markers"]

    locator_domain = "https://www.club4fitness.com"

    for store in stores:
        location_name = store["title"]
        if "opening soon" in location_name.lower():
            continue
        raw_address = store["address"].replace("Blvd, Su", "Blvd. Su").split(",")
        if "USA" in raw_address[-1].upper():
            raw_address.pop(-1)

        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[-1].strip()[:-6].strip()
        zip_code = raw_address[-1][-6:].strip()
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]

        if "http" not in store["link"]:
            link = (locator_domain + store["link"]).replace("comloc", "com/loc")
        else:
            link = store["link"]
        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        if "coming soon" in item.h1.text.lower():
            continue

        phone = (
            item.find("a", {"href": re.compile(r"tel.+")})
            .text.replace("Call", "")
            .strip()
        )

        try:
            hours_of_operation = " ".join(
                list(item.find(class_="dce-acf-repeater-list").stripped_strings)
            )
        except:
            hours_of_operation = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state.strip(),
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
