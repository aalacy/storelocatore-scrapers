from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data(sgw: SgWriter):
    locator_domain = "https://originalchopshop.com/"
    ext = "restaurant-locations/"

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locations = base.find_all("section")[1].find_all(class_="location")

    for loc in locations:
        content = list(loc.stripped_strings)
        location_name = content[0]
        phone_number = content[1]
        street_address = content[2]
        try:
            city, state, zip_code = addy_ext(content[3])
        except:
            street_address = content[1]
            city, state, zip_code = addy_ext(content[2])
            phone_number = "<MISSING>"

        hours = ""
        for h in content[6:]:
            hours += h + " "
        try:
            href = loc.a["href"]
            start_idx = href.find("/@")
            end_idx = href.find("z/data")
            if start_idx > 0:
                coords = href[start_idx + 2 : end_idx].split(",")
                lat = coords[0]
                longit = coords[1]
            else:
                lat = "<MISSING>"
                longit = "<MISSING>"
        except:
            lat = "<MISSING>"
            longit = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        if len(hours) < 2:
            hours = "<MISSING>"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
