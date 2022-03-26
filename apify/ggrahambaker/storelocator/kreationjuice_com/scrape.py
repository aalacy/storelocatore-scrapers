from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.kreationjuice.com/"
    ext = "pages/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    heading_list = base.find_all("h3")

    stores_lists = base.find(class_="rte").find_all("ul")

    for i, store_list in enumerate(stores_lists):
        try:
            location_type = heading_list[i].text
        except:
            pass
        stores = store_list.find_all("li")
        for store in stores:
            cont = list(store.stripped_strings)
            if len(cont) == 1:
                continue
            else:
                location_name = cont[0]
                if "," not in cont[1]:
                    location_name = location_name + cont[1]
                    cont.pop(1)
                if "from" in cont[2]:
                    cont.pop(2)

                addy = cont[1].split(",")
                street_address = " ".join(addy[:-2])
                city = addy[-2].strip()
                state = addy[-1].split()[0].strip()
                zip_code = addy[-1].split()[1].strip()

                if "Waterside" in street_address:
                    location_name = location_name + " Waterside"
                    street_address = street_address.replace("Waterside", "").strip()

                phone_number = cont[2]
                hours = cont[3]

                if "open" in phone_number.lower():
                    phone_number = cont[3]
                    hours = cont[2]

                store_number = "<MISSING>"
                lat = "<MISSING>"
                longit = "<MISSING>"

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
