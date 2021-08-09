from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    locator_domain = "http://eatmonterreys.com/"
    ext = "locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(locator_domain + ext, headers=headers)
    main = BeautifulSoup(req.text, "lxml")

    stores = main.tbody.find_all("tr")

    for store in stores:
        cont = store.find_all("td")
        city = cont[0].text.strip()
        street_address = cont[1].text.strip()
        state = cont[2].text.strip()
        zip_code = cont[3].text.strip()
        phone_number = cont[5].text.strip()

        href = cont[4].a["href"]

        start_idx = href.find("&sll=")
        end_idx = href.find("&sspn")
        if start_idx > 1:
            coords = href[start_idx + 5 : end_idx].split(",")
            lat = coords[0]
            longit = coords[1]
        else:
            lat = "<MISSING>"
            longit = "<MISSING>"

        location_name = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours = "<MISSING>"
        country_code = "US"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=locator_domain + ext,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
