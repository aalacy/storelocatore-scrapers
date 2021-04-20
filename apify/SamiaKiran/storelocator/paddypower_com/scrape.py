from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
##from sgzip.static import static_coordinate_list


session = SgRequests()
website = "paddypower_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def fetch_data():
    identities = set()
    if True:
##        coords = static_coordinate_list(radius=50, country_code=SearchableCountries.BRITAIN)
##        for lat, lng in coords:
        search = DynamicGeoSearch(country_codes=[SearchableCountries.BRITAIN], max_radius_miles=30, max_search_results=10)
        for lat, long in search:
            print(f'{(lat, long)} | remaining: {search.items_remaining()}')
            data='{"Latitude":"'+str(lat)+'","Longitude":"'+str(long)+'"}'
            url = "https://ppsl.s73.co/api/store/FindStores"
            loclist = session.post(url, data = data, headers=headers).json()
            for loc in loclist:
                location_name = loc["storeName"]
                store_number = loc["storeNumber"]
                latitude = loc["latitude"]
                longitude = loc["longitude"]
                phone = "<MISSING>"
                street_address = loc["address1"]
                city = loc["address2"]
                zip_postal = loc["postCode"]
                state = "<MISSING>"
                hours_of_operation=''
                for h in loc['outputHours']:
                    hours_of_operation=hours_of_operation+' '+h['days']+ ' '+ h['hours']
                identity = str(latitude)+','+str(longitude)+','+str(street_address)+','+str(zip_postal)
                if identity in identities:
                    continue
                log.info(location_name)
                identities.add(identity)
                yield SgRecord(
                    locator_domain="https://www.paddypower.com/",
                    page_url="https://locator.pponside.com/",
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code="US",
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type="<MISSING>",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
