from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="fultonbank.com")
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

logger = SgLogSetup().get_logger("fultonbank_com")


def fetch_data():
    url = "https://www.fultonbank.com/api/Branches/Search"
    payload = {
        "QueryModel.SearchTerm": "10001",
        "QueryModel.Radius": "5000",
    }
    r = session.post(url, headers=headers, data=payload)
    website = "fultonbank.com"
    typ = "<MISSING>"
    country = "US"
    addlist = []
    loc = "https://www.fultonbank.com/Maps-and-Locations"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "location-name" in line:
            items = line.split("location-name")
            for item in items:
                hours = ""
                if "location-address" in item:
                    name = (
                        item.split("\\u003e")[1]
                        .split("\\u003c")[0]
                        .replace("\\u0026amp;", "&")
                        .replace("\\u0026#39;", "'")
                    )
                    addinfo = (
                        item.split('on-address\\"\\u003e')[1]
                        .split("\\u003c/span")[0]
                        .replace("\\u0026#39;", "'")
                    )
                    addinfo = addinfo.replace("\\u0026amp;", "&")
                    raw_address = addinfo
                    add = addinfo.split(",")[0]
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip().split(" ")[0]
                    zc = addinfo.rsplit(" ", 1)[1]
                    try:
                        lat = item.split('data-lat=\\"')[1].split("\\")[0]
                        lng = item.split('data-long=\\"')[1].split("\\")[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    try:
                        phone = item.split("Phone:")[1].split("\\")[0].strip()
                    except:
                        phone = "<MISSING>"
                    days = item.split('"hours-row\\"\\u003e')
                    dc = 0
                    for day in days:
                        if "location-address" not in day:
                            hrs = day.split("\\")[0]
                            dc = dc + 1
                            if dc <= 7:
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                    addcity = add + "|" + city
                    if addcity not in addlist:
                        addlist.append(addcity)
                    if hours == "":
                        hours = "<MISSING>"
                    else:
                        yield SgRecord(
                            locator_domain=website,
                            page_url=loc,
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
                            raw_address=raw_address,
                        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
