from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.zerodegreescompany.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    locator_domain = "zerodegreescompany.com"

    items = base.find(id="Containerrda7c").find_all(class_="font_8")
    for i, item in enumerate(items):
        if "PLEASE SELECT" in item.text:
            items.pop(i)

    for i, item in enumerate(items):
        if i % 2 == 0:
            location_name = item.find_previous("h6").text
            raw_address = item.text.replace("Vegas ", "Vegas,").split(",")
            street_address = " ".join(raw_address[:-1])
            if "  " in street_address:
                city = street_address.split("  ")[-1].strip()
            else:
                city = street_address.split()[-1].strip()
            street_address = street_address.replace(city, "").replace("  ", " ").strip()
            state = raw_address[-1].split()[0].strip()
            zip_code = raw_address[-1].split()[1].strip()
        else:
            phone = item.text
            country_code = "US"
            location_type = "<MISSING>"
            store_number = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=base_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
