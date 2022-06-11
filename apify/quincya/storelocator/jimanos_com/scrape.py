from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.jimanos.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.findAll(class_="location-item-cell")

    for item in items:
        link = item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "jimanos.com"
        location_name = base.find("h1").text.strip()

        raw_data = list(
            base.find("span", attrs={"itemprop": "address"}).stripped_strings
        )
        street_address = raw_data[0]
        raw_line = raw_data[1]
        city = raw_line[: raw_line.rfind(",")].strip()
        state = location_name.split(",")[-1].strip()
        zip_code = raw_line[raw_line.rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = base.find("span", attrs={"itemprop": "telephone"}).text.strip()
        location_type = "<MISSING>"

        raw_gps = base.find("a", attrs={"id": "directions"})["href"]

        start_point = raw_gps.find("@") + 1
        latitude = raw_gps[start_point : raw_gps.find(",", start_point)]
        long_start = raw_gps.find(",", start_point) + 1
        longitude = raw_gps[long_start : raw_gps.find(",", long_start)]
        try:
            int(latitude[4:8])
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        hours_of_operation = " ".join(
            list(base.find("table", attrs={"class": "location-table"}).stripped_strings)
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
