from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


session = SgRequests()
website = "123pizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.241pizza.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_list = [
            "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=NMDTFZFIIJHWAFSC&center=53.9090049394,-106.133621976598&coordinates=49.630077061451715,-96.43269424222304,57.790455343073035,-115.83454971097284&multi_account=false&page=1&pageSize=60",
            "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=NMDTFZFIIJHWAFSC&center=49.4515636581,-84.2539813003493&coordinates=44.74424338570398,-74.55305356597442,53.746637758435554,-93.95490903472435&multi_account=false&page=1&pageSize=60",
            "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=NMDTFZFIIJHWAFSC&center=53.4604863996,-98.4703457399514&coordinates=49.137053662131905,-88.76941800557674,57.38451207065549,-108.17127347432641&multi_account=false&page=1&pageSize=60",
            "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=NMDTFZFIIJHWAFSC&center=52.7458531839,-60.0393930155171&coordinates=48.352142677956664,-50.33846528114168,56.73728524335223,-69.74032074989145&multi_account=false&page=1&pageSize=60",
        ]
        for search_url in search_list:
            stores_req = session.get(search_url, headers=headers).json()
            for store in stores_req:
                info = store["store_info"]
                title = info["name"]
                storeid = info["corporate_id"]
                street = info["address"]
                city = info["locality"]
                state = info["region"]
                pcode = info["postcode"]
                country = info["country"]
                phone = info["phone"]
                hours = info["store_hours"]
                lat = info["latitude"]
                lng = info["longitude"]
                link = "https://www.241pizza.com/" + store["llp_url"]
                hours = hours.split(";")
                hoo = ""
                for hr in hours:
                    hour = hr.split(",")
                    if len(hour) > 1:
                        day = hour[0]
                        start = hour[1]
                        end = hour[2]
                        if day == "1":
                            day = "Monday"
                        if day == "2":
                            day = "Tuesday"
                        if day == "3":
                            day = "Wednesday"
                        if day == "4":
                            day = "Thursday"
                        if day == "5":
                            day = "Friday"
                        if day == "6":
                            day = "Satday"
                        if day == "7":
                            day = "Sunday"
                        hoo = hoo + ", " + day + " " + start + " - " + end
                hoo = hoo.lstrip(", ").strip()

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code=country,
                    store_number=storeid,
                    phone=phone,
                    location_type=MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hoo.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
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
