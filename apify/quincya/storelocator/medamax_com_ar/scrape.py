from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.medamax.com.ar/sucursales.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.medamax.com.ar"

    items = base.find_all(class_="span12")

    for item in items:
        try:
            location_name = item.h1.text.strip()
            raw_address = item.find_all("h1")[1].text + " " + location_name
        except:
            continue

        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode

        if not city:
            city = location_name

        country_code = "AR"
        store_number = ""
        location_type = ""
        raw_data = list(item.h3.stripped_strings)
        phone = raw_data[0].split("/")[0].replace("Tel.", "").split("INT")[0].strip()
        try:
            hours_of_operation = raw_data[1].split(": ")[1].strip()
        except:
            hours_of_operation = list(item.stripped_strings)[-1].split(": ")[1].strip()
        map_link = item.iframe["src"]
        lat_pos = map_link.rfind("!3d")
        latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
        lng_pos = map_link.find("!2d")
        longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        if len(latitude) > 50:
            geo = map_link.split("&ll=")[1].split("&")[0].split(",")
            latitude = geo[0]
            longitude = geo[1]

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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
