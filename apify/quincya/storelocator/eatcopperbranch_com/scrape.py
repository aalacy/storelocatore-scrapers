from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://eatcopperbranch.com/locations/"

    locator_domain = "https://eatcopperbranch.com"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "html.parser")

    items = base.find_all("li", class_="fusion-layout-column")

    for item in items:
        raw_address = list(item.stripped_strings)
        location_name = raw_address[0]
        street_address = raw_address[1]
        if "," in street_address:
            if "suite" not in street_address and "16th" not in street_address:
                street_address = street_address.split(",")[0].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city_line = raw_address[2].split(",")
        if len(city_line) == 3:
            city = city_line[0].strip()
            state = city_line[1].strip()
            zip_code = city_line[2].strip()
        else:
            city = city_line[0].strip()
            state = city_line[1].split()[0].strip()
            zip_code = " ".join(city_line[1].split()[1:])
        if len(zip_code) == 5:
            country_code = "US"
        else:
            country_code = "CA"

        phone = raw_address[3]
        if "-" not in phone:
            phone = ""
        location_type = ""
        latitude = ""
        longitude = ""

        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "html.parser")

        store_number = base.main.section.div["id"].split("-")[-1]
        hours_of_operation = " ".join(
            list(
                base.main.section.find(string="Opening Hours")
                .find_previous(class_="fusion-column-wrapper")
                .find_previous(class_="fusion-column-wrapper")
                .stripped_strings
            )[1:]
        )
        if hours_of_operation.find("Temporarily Closed") != -1:
            hours_of_operation = "Temporarily Closed"
        if hours_of_operation.find("COMING SOON") != -1:
            hours_of_operation = "COMING SOON"
        if hours_of_operation.find("Coming soon") != -1:
            hours_of_operation = "Coming soon"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
