from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.iaai.com/branchlocations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="table-row table-row-border")

    for item in items:
        locator_domain = "iaai.com"
        location_name = item.find(class_="heading-7").text.strip()

        raw_address = (
            item.find(class_="data-list__value")
            .text.replace("\n", "")
            .replace("Center, Tenth", "Center Tenth")
            .split(",")
        )

        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2][: raw_address[2].rfind(" ")].strip()
        zip_code = raw_address[2][raw_address[2].rfind(" ") + 1 :].strip()

        country_code = "US"

        if state == "AE":
            country_code = state
            state = ""
        phone = item.find_all(class_="data-list__value")[1].text

        location_type = "<MISSING>"
        hours_of_operation = item.find_all(class_="data-list__value")[4].text.strip()

        link = "https://www.iaai.com" + item.find(class_="heading-7")["href"]

        store_number = link.split("/")[-1]

        # Get lat/long
        req = session.get(link, headers=headers)
        maps = BeautifulSoup(req.text, "lxml")

        try:
            latitude = maps.find(id="BranchModel")["data-latitude"]
            longitude = maps.find(id="BranchModel")["data-longitude"]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if country_code == "AE":
            hours_of_operation = (
                " ".join(maps.find(class_="col-md-12 mb-20").p.text.split("\r\n")[1:-1])
                .replace("  ", " ")
                .strip()
            )
            phone = (
                maps.find(class_="col-md-12 mb-20")
                .p.text.split("\r\n")[-1]
                .split(":")[1]
                .strip()
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
