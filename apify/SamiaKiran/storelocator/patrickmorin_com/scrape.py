import json
import datetime
import calendar
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "patrickmorin_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://patrickmorin.com/"
MISSING = "<MISSING>"


def findDay(date):
    born = datetime.datetime.strptime(date, "%d %m %Y").weekday()
    return calendar.day_name[born]


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    url = "https://www.patrickmorin.com/fr/magasins"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"markers":')[1].split(',"type"')[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        page_url = loc["url"]
        store_number = loc["id"]
        location_name = loc["name"]
        phone = loc["telephone"]
        latitude = loc["latitude"]
        longitude = loc["longitude"]
        location_name = strip_accents(location_name)
        log.info(page_url)
        hour_list = loc["schedule"]["calendar"]["opening-hours"]
        hours_of_operation = ""
        temp_list = []
        for hour in hour_list:
            temp = hour.split("-")
            day = findDay(temp[2] + " " + temp[1] + " " + temp[0])
            temp_2 = (
                str(hour_list[hour]).replace("]", "").replace("[", "").replace("'", '"')
            )
            try:
                temp_2 = json.loads(temp_2)
                start = temp_2["start_time"]
                end = temp_2["end_time"]
                variable = day + " " + start + " - " + end
                if variable in temp_list:
                    continue
                temp_list.append(variable)
                hours_of_operation = hours_of_operation + " " + variable

            except:
                hours_of_operation = hours_of_operation + " " + day + ": Closed"
        raw_address = loc["address"]
        address = raw_address.split(",")
        street_address = address[0] + " " + address[1]
        city = address[2]
        state = MISSING
        zip_postal = address[3]
        country_code = address[-1]
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city,
            state=state.strip(),
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
