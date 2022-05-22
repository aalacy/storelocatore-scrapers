from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://thehumanbean.com/find/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base_str = str(BeautifulSoup(req.text, "lxml"))

    js = (
        base_str.split("location_data = new Array();")[1]
        .split("map_0")[0]
        .replace("location_data.push(", "")
        .replace(");", "")
        .replace("\t", "")
        .replace("\n", "")
        .replace("'", '"')
        .replace("\\", "")
        .strip()
    )

    stores = js.split('{"name":')[1:]

    locator_domain = "https://thehumanbean.com/"

    for store in stores:
        location_name = (
            store.split('",')[0].replace("&#8211;", "-").replace('"', "").strip()
        )
        street_address = store.split('street-address">')[1].split("<")[0]
        street_address = street_address.split(", Tucson")[0].split(", Yakima")[0]
        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        city = store.split('locality">')[1].split("<")[0].replace("&#039;", "'").strip()
        state = location_name.split("-")[0].strip()
        if "Human Bean" in state:
            state = state.split()[-1]
        zip_code = store.split('postal-code">')[1].split("<")[0].strip()
        country_code = "US"
        store_number = store.split("wpseo_location-")[1].split('"')[0].strip()
        phone = store.split('"phone": "')[1].split('"')[0].strip()
        location_type = ""
        latitude = store.split('"lat":')[1].split(",")[0].strip()
        longitude = store.split('"long":')[1].split(",")[0].strip()
        link = store.split('"url":')[1].split(",")[0].replace('"', "").strip()

        hours_of_operation = ""
        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            if "coming soon" in base.h2.text.lower():
                continue
            hours_of_operation = " ".join(
                list(base.find(class_="wpseo-opening-hours").stripped_strings)
            )
            if "location for" in hours_of_operation:
                hours_of_operation = ""
        except:
            pass

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
