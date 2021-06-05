import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "rustytaco_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    url = "https://rustytaco.com/locations-search/"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split("window.gmaps.items =")[1].split(
        "window.gmaps.order_url = ", 1
    )[0]
    loclist = loclist.replace(";", "").strip()
    loclist = json.loads(loclist)
    for loc in loclist:
        page_url = loc["detailPageUrl"]
        store_number = loc["id"]
        location_name = loc["name"]
        log.info(location_name)
        latitude = loc["lat"]
        longitude = loc["lng"]
        street_address = loc["custom_fields"]["address"]["street"]
        city = loc["custom_fields"]["address"]["city"]
        state = loc["custom_fields"]["address"]["state"]
        zip_postal = loc["custom_fields"]["address"]["zip"]
        phone = loc["custom_fields"]["phone"]
        if not phone:
            phone = "<MISSING>"
        hour_list = loc["custom_fields"]["hours"]
        if hour_list is False:
            hours_of_operation = "<MISSING>"
        else:
            hours_of_operation = " "
            for hour in hour_list:
                open_time = hour["open_time"]
                close_time = hour["close_time"]
                day = hour["day"]
                hours_of_operation = (
                    hours_of_operation + day + " " + open_time + " " + close_time + " "
                )
        yield SgRecord(
            locator_domain="https://rustytaco.com/",
            page_url=page_url,
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
