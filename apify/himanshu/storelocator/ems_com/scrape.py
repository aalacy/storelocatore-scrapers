from sgrequests import SgRequests
from sglogging import sglog
import re
import json
import cloudscraper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ems.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
session = cloudscraper.create_scraper(sess=session)


def fetch_data():
    base_url = "https://www.ems.com/find-a-store"
    r = session.get(base_url)
    json_text = None
    try:
        json_text = (
            r.text.split('window.App["stores"]=')[1]
            .strip()
            .split(";</script>")[0]
            .strip()
        )
    except:
        pass

    if json_text:
        for i in json.loads(json_text):
            locator_domain = website
            location_name = i["title"]
            city = i["addressLocality"]
            state = i["addressRegion"]
            zip = i["addressPostalCode"]
            street_address = (
                re.sub(r"\s+", " ", i["address"])
                .replace(", Hadley MA 01035", "")
                .replace(", North Conway, NH 03860", "")
                .replace(", North Conway, NH 03860", "")
                .replace("Peterborough NH 03458", "")
                .replace(" NY 12946", "")
                .replace(", Warwick RI 02889", "")
                .replace(
                    " ".join(
                        [
                            word.capitalize()
                            for word in " ".join(city.split("-")).split(" ")
                        ]
                    ),
                    "",
                )
                .replace(" , MA, 01752", "")
                .replace(state, "")
                .replace(zip, "")
                .strip()
            )

            country_code = i["country"].replace("Un", "US")
            store_number = i["legacyId"]
            phone = i["telephone"]
            location_type = "Eastern Mountain Sports"
            latitude = str(i["coordinates"]["lat"])
            longitude = str(i["coordinates"]["lng"])
            page_url = "https://www.ems.com/stores/" + i["slug"].lower()
            if i["communication"] == "Coming Soon!":
                continue
            hours_list = []
            hour = i["hoursOfOperation"]
            for h in hour:
                time = h["open"] + " - " + h["closed"]
                hours_list.append(h["day"] + ": " + time)

            hours_of_operation = "; ".join(hours_list).strip()
            if "753 Donald J. Lynch Boulevard Marlborough, MA, 01752" in street_address:
                street_address = "753 Donald J. Lynch Boulevard Marlborough"

            street_address = street_address.replace(" , MA, 01752", "").replace(
                ", Freeport ME", ""
            )
            if street_address[-1] == ",":
                street_address = "".join(street_address[:-1]).strip()

            yield SgRecord(
                locator_domain=locator_domain,
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

    else:
        log.info(r.text)


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
