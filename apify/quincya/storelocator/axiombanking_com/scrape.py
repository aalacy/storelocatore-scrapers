import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.axiombanking.com/about-us/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "axiombanking.com"

    script = base.find(id="location_finder-js-extra").contents[0].strip()

    js = (
        script.split("location_Finder = {")[1]
        .split('location_coordinates":')[1]
        .split(',"location_titles')[0]
        .strip()
    )
    coords = json.loads(js)

    js = script.split('location_titles":')[1].split(',"location_desc')[0].strip()
    titles = json.loads(js)

    js = script.split('location_desc":')[1].split(',"location_types')[0].strip()
    details = json.loads(js)

    for i in range(len(coords)):
        location_name = titles[i]["title"]
        item = BeautifulSoup(details[i]["info"], "lxml")
        if "," in item.p.text:
            raw_address = item.p.text.split("\n")
            phone = item.find_all("p")[1].text.replace("Phone:", "").strip()
            hours_of_operation = item.find_all("p")[2].text.replace("\n", " ").strip()
        else:
            raw_address = item.find_all("p")[1].text.split("\n")
            phone = item.find_all("p")[2].text.replace("Phone:", "").strip()
            hours_of_operation = item.find_all("p")[3].text.replace("\n", " ").strip()

        street_address = raw_address[0]
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[1].split()[0]
        zip_code = raw_address[1].split(",")[1].split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        latitude = coords[i]["lat"]
        longitude = coords[i]["lng"]

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
