from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://stonefiregrill.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find("ul", attrs={"class": "location_grid clearfix"}).find_all("li")

    for item in items:

        link = item.find("a")["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "stonefiregrill.com"
        content = base.find("div", attrs={"class": "row"})
        location_name = content.find("h1").text.strip()
        street_address = content.find("span", attrs={"class": "address"}).text.strip()
        raw_line = base.find("span", attrs={"class": "city"}).text.strip()
        city = raw_line[: raw_line.rfind(",")].strip()
        state = raw_line[raw_line.rfind(",") + 1 : raw_line.rfind(" ")].strip()
        zip_code = raw_line[raw_line.rfind(" ") + 1 :].strip()
        if state == "":
            state = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = base.find("span", attrs={"class": "phone strong"}).text.strip()
        location_type = "<MISSING>"

        script = str(base.find(id="wpsl-js-js-extra"))
        latitude = script.split('"lat":"')[1].split('",')[0]
        longitude = script.split('"lng":"')[1].split('",')[0]

        hours_of_operation = " ".join(
            list(
                content.find(
                    "table", attrs={"class": "wpsl-opening-hours"}
                ).stripped_strings
            )
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
