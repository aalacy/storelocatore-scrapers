import json
import time

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    base_url = "https://www.citymarket.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    soup = BeautifulSoup(
        session.get(
            "https://www.citymarket.com/storelocator-sitemap.xml", headers=headers
        ).text,
        "lxml",
    )
    for url in soup.find_all("loc")[:-1]:
        page_url = url.text
        for i in range(6):
            try:
                req = session.get(page_url, headers=headers)
                location_soup = BeautifulSoup(req.text, "lxml")
                script = location_soup.find(
                    "script", attrs={"type": "application/ld+json"}
                ).contents[0]
                break
            except:
                time.sleep(10)
                session = SgRequests()
        data = json.loads(script)
        location_name = location_soup.find(
            "h1", {"data-qa": "storeDetailsHeader"}
        ).text.strip()

        try:
            street_address = data["address"]["streetAddress"]
            city = data["address"]["addressLocality"]
            state = data["address"]["addressRegion"]
            zipp = data["address"]["postalCode"]
        except:
            raw_address = (
                location_soup.find(class_="StoreAddress-storeAddressGuts")
                .get_text(" ")
                .replace(",", "")
                .replace("5448  West", "5448 West")
                .replace(" .", ".")
                .replace("..", ".")
                .split("  ")
            )
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].strip()
            zipp = raw_address[3].split("Get")[0].strip()
        country_code = "US"
        store_number = page_url.split("/")[-1]
        phone = data["telephone"]
        location_type = "<MISSING>"
        lat = data["geo"]["latitude"]
        lng = data["geo"]["longitude"]
        hours = " ".join(data["openingHours"])
        hours = (
            hours.replace("Su-Sa", "Sun - Sat:")
            .replace("Su-Fr", "Sun - Fri:")
            .replace("-00:00", " - Midnight")
            .replace("Su ", "Sun")
            .replace("Sun1", "Sun 1")
            .replace("Mo-Fr", "Mon - Fri")
            .replace("Sa ", "Sat ")
            .replace("SunCLOSED", "Sun CLOSED")
            .replace("  ", " ")
        ).strip()
        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
