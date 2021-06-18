from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

logger = SgLogSetup().get_logger("chevronwithtechron_com")
session = SgRequests()

addresses = []


def fetch_records_for(coords):
    latt = coords[0]
    long = coords[1]
    logger.info(f"pulling records for coordinates: {latt,long}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    stores = None
    try:
        r = session.get(
            "https://www.chevronwithtechron.com/webservices/ws_getChevronTexacoNearMe_r2.aspx?lat="
            + str(latt)
            + "&lng="
            + str(long)
            + "&oLat="
            + str(latt)
            + "&oLng="
            + str(long)
            + "&brand=chevronTexaco&radius=35",
            headers=headers,
        )
        stores = r.json()["stations"]
    except:
        pass
    return stores


def process_record(raw_results_from_one_coordinate):
    data = raw_results_from_one_coordinate
    if data is not None:
        for store_data in data:
            latitude = store_data["lat"]
            longitude = store_data["lng"]
            locator_domain = "https://www.chevronwithtechron.com"
            location_name = store_data["name"]
            street_address = store_data["address"]
            if street_address in addresses:
                continue
            addresses.append(street_address)
            city = store_data["city"]
            state = store_data["state"]
            zipp = store_data["zip"]
            country_code = "US"
            store_number = store_data["id"]
            phone = (
                store_data["phone"].replace(".", "")
                if "phone" in store_data and store_data["phone"]
                else "<MISSING>"
            )

            location_type = "<MISSING>"
            hours_of_operation = (
                store_data["hours"] if store_data["hours"] else "<MISSING>"
            )
            page_url = f"https://www.chevronwithtechron.com/station/{street_address.replace(' ','-')}-{city.replace(' ','-')}-{state}-{zipp}-id{store_number}"

            yield SgRecord(
                locator_domain=locator_domain,
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
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = parallelize(
            search_space=static_coordinate_list(
                radius=5, country_code=SearchableCountries.USA
            ),
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=20,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
