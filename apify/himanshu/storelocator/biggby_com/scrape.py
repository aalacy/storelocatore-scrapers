from sglogging import sglog
from bs4 import BeautifulSoup
from datetime import datetime
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "biggby_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.biggby.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.biggby.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("marker")
    for i in data:
        if i["coming-soon"] == "yes":
            continue
        location_name = i["name"]
        log.info(location_name)
        street_address = i["address-one"] + " " + i["address-two"]
        city = i["city"]
        state = i["state"]
        zip_postal = i["zip"]
        store_number = i["id"]
        try:
            latitude = i["lat"]
            longitude = i["lng"]
        except KeyError:
            latitude = MISSING
            longitude = MISSING
        country_code = i["country"]
        hours = ""
        if i["mon-thurs-open-hour"]:
            try:
                mon_o = datetime.strptime(str(i["mon-thurs-open-hour"]), "%H:%M")
                mon_open = mon_o.strftime("%I:%M %p")
            except:
                mon_o = datetime.strptime(str(i["mon-thurs-open-hour"]), "%H")
                mon_open = mon_o.strftime("%I:%M %p")
        else:
            mon_open = "close"

        if i["mon-thurs-close-hour"]:
            try:
                mon_c = datetime.strptime(str(i["mon-thurs-close-hour"]), "%H:%M")
                mon_close = mon_c.strftime("%I:%M %p")
            except:
                mon_c = datetime.strptime(str(i["mon-thurs-close-hour"]), "%H")
                mon_close = mon_c.strftime("%I:%M %p")
        else:
            mon_close = "close"

        if i["fri-open-hour"]:
            try:
                fir_o = datetime.strptime(str(i["fri-open-hour"]), "%H:%M")
                fri_open = fir_o.strftime("%I:%M %p")
            except:
                fir_o = datetime.strptime(str(i["fri-open-hour"]), "%H")
                fri_open = fir_o.strftime("%I:%M %p")
        else:
            fri_open = "close"

        if i["fri-close-hour"]:
            try:
                fri_c = datetime.strptime(str(i["fri-close-hour"]), "%H:%M")
                fri_close = fri_c.strftime("%I:%M %p")
            except:
                mon_c = datetime.strptime(str(i["fri-close-hour"]), "%H")
                fri_close = fri_c.strftime("%I:%M %p")
        else:
            fri_close = "close"

        if i["sat-open-hour"]:
            try:
                sat_o = datetime.strptime(str(i["sat-open-hour"]), "%H:%M")
                sat_open = sat_o.strftime("%I:%M %p")
            except:
                sat_o = datetime.strptime(str(i["sat-open-hour"]), "%H")
                sat_open = sat_o.strftime("%I:%M %p")
        else:
            sat_open = "close"

        if i["sat-close-hour"]:
            try:
                sat_c = datetime.strptime(str(i["sat-close-hour"]), "%H:%M")
                sat_close = sat_c.strftime("%I:%M %p")
            except:
                sat_c = datetime.strptime(str(i["sat-close-hour"]), "%H")
                sat_close = sat_c.strftime("%I:%M %p")
        else:
            sat_close = "close"

        if i["sun-open-hour"]:
            try:
                sun_o = datetime.strptime(str(i["sun-open-hour"]), "%H:%M")
                sun_open = sun_o.strftime("%I:%M %p")
            except:
                sun_o = datetime.strptime(str(i["sun-open-hour"]), "%H")
                sun_open = sun_o.strftime("%I:%M %p")
        else:
            sun_open = "close"

        if i["sun-close-hour"]:
            try:
                sun_c = datetime.strptime(str(i["sun-close-hour"]), "%H:%M")
                sun_close = sun_c.strftime("%I:%M %p")
            except:
                sun_c = datetime.strptime(str(i["sun-close-hour"]), "%H")
                sun_close = sun_c.strftime("%I:%M %p")
        else:
            sun_close = "close"
        hours = (
            "mon to thurs"
            + " "
            + str(mon_open)
            + "-"
            + str(mon_close)
            + ","
            + "fri"
            + " "
            + str(fri_open)
            + "-"
            + str(fri_close)
            + ","
            + "sat"
            + " "
            + str(sat_open)
            + "-"
            + str(sat_close)
            + ","
            + "sun"
            + " "
            + str(sun_open)
            + "-"
            + str(sun_close)
        )
        hours_of_operation = hours.replace("close-close", "close").replace(",", ", ")
        phone = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
