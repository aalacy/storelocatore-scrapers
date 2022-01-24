from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://hurst-iw.co.uk/pages/store-opening-times-and-addresses"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="rte").find_all("p")
    locator_domain = "https://hurst-iw.co.uk"

    street_address = ""
    city = ""
    state = ""
    zip_code = ""
    country_code = ""
    store_number = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for item in items:
        if not hours_of_operation:
            if "hours are" in item.text:
                hours_of_operation = item.text.split("hours are")[1].strip()
        else:
            rows = item.find_all("span")
            started = False
            phone = ""
            for row in rows:
                if row.strong:
                    if not started:
                        location_name = row.strong.text
                        started = True
                    else:
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
                        started = False
                        phone = ""
                        location_name = row.strong.text
                elif "PO" in row.text[:2]:
                    zip_code = row.text
                elif "tel" in row.text.lower():
                    phone = row.text.split(":")[1].strip()
                elif "street" in row.text.lower() or "road" in row.text.lower():
                    street_address = row.text
                    city = location_name.title().split("&")[0].strip()
                    state = ""
                    country_code = "GB"
                    location_type = ""
                    store_number = ""
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                if phone:
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
