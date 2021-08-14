from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.club4fitness.com/location/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "club4fitness.com"

    items = base.find_all("article")
    geos = base.find(class_="acf-map").find_all("div")

    for i in items:
        location_name = i.a.text
        if "opening soon" in location_name.lower():
            continue
        link = i.a["href"]
        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        raw_address = (
            i.find_all(class_="elementor-widget-container")[-1]
            .text.replace(", Suite", " Suite")
            .replace(", USA", "")
            .replace("Ridgeland", ", Ridgeland")
            .split(",")
        )
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        if len(raw_address) == 4:
            state = raw_address[2]
            zip_code = raw_address[3]
        if len(raw_address) == 3:
            state = raw_address[-1].split()[0]
            zip_code = raw_address[-1].split()[1]
        country_code = "US"
        store_number = i["id"].split("-")[1]
        phone = (
            item.main.find(class_="elementor-button-text")
            .text.replace("Call", "")
            .strip()
        )
        location_type = "<MISSING>"

        try:
            hours_of_operation = " ".join(
                list(item.find(class_="dce-acf-repater-list").stripped_strings)
            )
        except:
            hours_of_operation = "<MISSING>"
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"
        for geo in geos:
            url = geo.strong.text
            if url in link:
                latitude = geo["data-lat"]
                longitude = geo["data-lng"]
                break

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state.strip(),
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
