import re

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.yourwirelessinc.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()["markers"]

    locator_domain = "yourwirelessinc.com"

    for store in store_data:
        location_name = store["title"]
        raw_address = store["address"]
        street_address = raw_address[: raw_address.rfind(location_name)].strip()
        city = location_name
        state = raw_address.split(",")[-1].split()[0]
        zip_code = raw_address.split(",")[-1].split()[1]
        country_code = "US"
        store_number = store["id"]

        try:
            phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", store["description"])[0]
        except:
            try:
                phone = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", store["description"])[
                    0
                ]
            except:
                phone = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lng"]

        link = "https://www.yourwirelessinc.com/locations/"
        if store["link"]:
            link = ("https://www.yourwirelessinc.com" + store["link"]).replace(
                "locations", "locations-and-team-members"
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
