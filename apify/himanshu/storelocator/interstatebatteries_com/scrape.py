from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name="interstatebatteries.com")


def fetch_data():
    base_url = "https://interstatebatteries.com"
    slug_list = ["/distributor-locations", "/all-battery-center-locations"]
    for slug in slug_list:
        r = session.get(base_url + slug)
        soup = BeautifulSoup(r.text, "lxml")
        main = (
            soup.find("div", {"class": "store-directory"})
            .find("ul", {"class": "list"})
            .find_all("a")
        )
        for dt in main:
            if re.search("/locations/", dt["href"]):
                try:
                    r1 = session.get(base_url + dt["href"])
                    log.info(base_url + dt["href"])
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    if (
                        "Sorry, but the page you are looking for can't be found."
                        not in soup1.text
                    ):
                        store_json = json.loads(
                            r1.text.split("window.localstoreinfo = ")[1]
                            .strip()
                            .split("</script>")[0]
                            .replace(";", "")
                            .strip()
                        )

                        location_name = store_json["Name"]
                        if "Of" in location_name:
                            location_name = location_name.split("Of")[0].strip()

                        elif "of" in location_name:
                            location_name = location_name.split("of")[0].strip()

                        if "Distributor" in location_name:
                            location_name = "Interstate Batteries Distributor"

                        if "All Battery Center" in location_name:
                            location_name = "Interstate All Battery Center"

                        street_address = store_json["Address1"]
                        if (
                            store_json["Address2"] is not None
                            and len(store_json["Address2"]) > 0
                        ):
                            street_address = (
                                street_address + ", " + store_json["Address2"]
                            )
                        city = store_json["City"]
                        state = store_json["State"]
                        zip = store_json["PostalCode"]
                        if not zip:
                            country_code = "<MISSING>"
                        elif bool(re.search("[a-zA-Z]", zip)):
                            country_code = "CA"
                        else:
                            country_code = "US"
                        phone = store_json["Phone"]
                        location_type = slug.replace("/", "").strip()
                        latitude = store_json["PinLatitude"]
                        longitude = store_json["PinLongitude"]
                        store_number = store_json["id"]
                        hours = store_json["DetailedHours"]
                        hours_list = []
                        if hours is not None:
                            hours_of_operation = ""
                            for hour in hours:
                                day = hour["Day"]
                                if hour["IsClosed"] is True:
                                    time = "Closed"
                                else:
                                    time = hour["Hours"]
                                hours_list.append(day + ":" + time)

                        hours_of_operation = "; ".join(hours_list).strip()
                        page_url = base_url + dt["href"]
                        yield SgRecord(
                            locator_domain="https://interstatebatteries.com",
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip,
                            country_code=country_code,
                            store_number=store_number,
                            phone=phone,
                            location_type=location_type,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours_of_operation,
                        )

                except:
                    continue


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
