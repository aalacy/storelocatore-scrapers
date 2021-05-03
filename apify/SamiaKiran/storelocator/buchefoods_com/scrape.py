from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "buchefoods_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        data = {
            "apiurl": "https://buchefoods.rsaamerica.com/Services/SSWebRestApi.svc/GetClientStores/1"
        }
        url = "https://buchefoods.com/ajax/index.php"
        loclist = session.post(url, data=data, headers=headers).json()[
            "GetClientStores"
        ]
        for loc in loclist:
            location_name = loc["ClientStoreName"]
            log.info(location_name)
            street_address = loc["AddressLine1"] + " " + loc["AddressLine2"]
            city = loc["City"]
            state = loc["StateName"]
            zip_postal = loc["ZipCode"]
            phone = loc["StorePhoneNumber"]
            store_number = loc["StoreNumber"]
            latitude = loc["Latitude"]
            longitude = loc["Longitude"]
            hours_of_operation = loc["StoreTimings"]
            yield SgRecord(
                locator_domain="https://buchefoods.com/",
                page_url="https://buchefoods.com/contact",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
