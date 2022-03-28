from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://jordanskwikstopinc.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("div", attrs={"style": "font-size:1.6em"})
    locator_domain = "jordanskwikstopinc.com"

    for item in items:

        raw_data = (
            str(item.p)
            .replace("<p>", "")
            .replace("</p>", "")
            .replace(" AR ", ",AR ")
            .replace(",,", ",")
            .split("<br/>")
        )
        location_name = item.a.text.strip()
        street_address = raw_data[0].replace(",", "").strip()
        city = raw_data[1].split(",")[0].strip()
        state = raw_data[1].split(",")[1].strip().split()[0]
        zip_code = raw_data[1].split(",")[1].strip().split()[1]
        country_code = "US"
        store_number = location_name.split("#")[-1]
        location_type = "<MISSING>"
        phone = "<MISSING>"
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
