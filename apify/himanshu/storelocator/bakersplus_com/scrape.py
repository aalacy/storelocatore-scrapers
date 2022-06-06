import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("bakersplus.com")


def fetch_data(sgw: SgWriter):

    base_url = "https://www.bakersplus.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"user-agent": user_agent}

    base_link = "https://www.bakersplus.com/storelocator-sitemap.xml"
    with SgRequests() as http:
        r = http.get(base_link, headers=headers)
        print(f"HTTPStatusCode:{r.status_code}")
        soup = BeautifulSoup(r.text, "lxml")

        for url in soup.find_all("loc")[:-1]:
            page_url = url.text
            for i in range(6):
                log.info(page_url)
                req = http.get(page_url, headers=headers)
                location_soup = BeautifulSoup(req.text, "lxml")

                location_name = ""
                try:
                    script = location_soup.find(
                        "script", attrs={"type": "application/ld+json"}
                    ).contents[0]
                    data = json.loads(script)
                    street_address = data["address"]

                    location_name = location_soup.find(
                        "h1", {"data-qa": "storeDetailsHeader"}
                    ).text.strip()

                    if location_name:
                        log.info(location_name)
                        break
                except:
                    log.info("Retrying ..")

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
            lat = data["geo"]["latitude"]
            lng = data["geo"]["longitude"]
            hours = " ".join(data["openingHours"])

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
                    location_type="",
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
