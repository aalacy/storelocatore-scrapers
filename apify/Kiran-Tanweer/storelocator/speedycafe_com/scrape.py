from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()
website = "speedycafe_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

DOMAIN = "https://speedycafe.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
        search_url = "https://www.speedway.com/locations/search"
        for lat, lng in search:
            payload = (
                "SearchType=search&SearchText=&StartIndex=0&Limit=5000&Latitude="
                + str(lat)
                + "&Longitude="
                + str(lng)
                + "&Radius=20000&Filters%5BFuelType%5D=Unleaded&Filters%5BOnlyFavorites%5D=false&Filters%5BAmenities%5D%5B%5D=A_0&Filters%5BText%5D="
            )
            stores_req = session.post(search_url, headers=headers, data=payload)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            locations = soup.findAll(
                "section", {"class": "c-location-card c-location-card--cafe"}
            )
            for item in locations:
                latitude = item["data-latitude"]
                longitude = item["data-longitude"]
                search.found_location_at(float(latitude), float(longitude))
                link = DOMAIN + item.a["href"]
                street = item.find(class_="c-location-heading").text.strip()
                city = item.find(
                    "li", attrs={"data-location-details": "address"}
                ).text.split(",")[0]
                state = item["data-state"]
                zip_code = (
                    item.find("li", attrs={"data-location-details": "address"})
                    .text.split(",")[-1]
                    .split()[-1]
                )
                country = "US"
                store_number = item["data-costcenter"]
                hours_of_operation = ""
                try:
                    if (
                        "open 24"
                        in item.find(
                            class_="c-location-options--amenities"
                        ).text.lower()
                    ):
                        hours_of_operation = "Open 24 Hours"
                except:
                    hours_of_operation = MISSING
                try:
                    phone = item.find(
                        "li", attrs={"data-location-details": "phone"}
                    ).text.strip()
                    if not phone:
                        phone = MISSING
                except:
                    phone = MISSING

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=link,
                    location_name="Speedy Café",
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_code,
                    country_code=country,
                    store_number=store_number,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.STORE_NUMBER})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
