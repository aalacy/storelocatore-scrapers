from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("pandaexpress_ca")
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}

session = SgRequests()


def fetch_records():
    locs = []
    api_endpoint_url = "https://www.pandaexpress.ca/en/userlocation/searchbycoordinates?lat=34.0667&lng=-118.0833&limit=1000&hours=true&_=1582854262229"
    r = session.get(api_endpoint_url, headers=headers)
    for line in r.iter_lines():
        line = str(line)
        items = line.split('"Id":')
        for item in items:
            if '"Company":' in item:
                if '"Country":"Canada"' in item:
                    store = item.split(",")[0]
                    website = "pandaexpress.ca"
                    loc = "<MISSING>"
                    name = item.split('"Name":"')[1].split('"')[0]
                    add = item.split('"Address":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    try:
                        state = item.split('"State":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    try:
                        zc = item.split('"Zip":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    phone = item.split('"Phone":"')[1].split('"')[0]
                    country = "CA"
                    typ = "<MISSING>"
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    try:
                        hours = (
                            "Mon: "
                            + item.split('"Monday":{"StartTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"Monday":{')[1]
                            .split(',"EndTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Tue: "
                            + item.split('"Tuesday":{"StartTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"Tuesday":{')[1]
                            .split(',"EndTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item.split('"Wednesday":{"StartTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"Wednesday":{')[1]
                            .split(',"EndTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item.split('"Thursday":{"StartTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"Thursday":{')[1]
                            .split(',"EndTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item.split('"Friday":{"StartTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"Friday":{')[1]
                            .split(',"EndTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item.split('"Saturday":{"StartTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"Saturday":{')[1]
                            .split(',"EndTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sun: "
                            + item.split('"Sunday":{"StartTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"Sunday":{')[1]
                            .split(',"EndTime":"')[1]
                            .split('"')[0]
                        )
                    except:
                        hours = ""
                    if hours == "":
                        hours = "<MISSING>"
                    if city == "Edmonton" or city == "Calgary":
                        state = "AB"
                    if city == "Toronto":
                        state = "ON"
                    item = SgRecord(
                        locator_domain="pandaexpress.ca/en/",
                        page_url="",
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        store_number=store,
                        phone=phone,
                        location_type=typ,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours,
                        raw_address="",
                    )

                    logger.info(f"ITEM: {item.as_dict()}")
                    yield item


def scrape():
    logger.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
    )
    with SgWriter(deduper) as writer:
        results = fetch_records()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
