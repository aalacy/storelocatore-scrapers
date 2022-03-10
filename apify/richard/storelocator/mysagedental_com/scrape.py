from sgrequests import SgRequests, SgRequestError
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog
import lxml.html

URL = "https://mysagedental.com/"
website = "mysagedental.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # store data

    base_link = "https://mysagedental.com/wp-admin/admin-ajax.php?action=load_locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["locations_all"]

    for store in stores:
        # Store ID
        location_id = store["id"]

        # Type
        location_type = "<MISSING>"

        # Name
        location_title = store["title"]
        if "coming soon" in location_title.lower():
            continue

        # Page url
        page_url = (
            URL
            + location_title.lower()
            .split("(")[0]
            .replace("east boca", "boca")
            .replace("hallandale beach", "hallandale")
            .split("at 7")[0]
            .strip()
            .replace(" ", "-")
            .replace(".", "-")
            .strip()
        )

        # Street
        street_address = store["address_1"].strip()

        # city
        city_line = store["address"].strip().split(",")
        city = city_line[0].strip()

        # zip
        zipcode = city_line[-1].strip().split()[1].strip()

        # State
        state = city_line[-1].strip().split()[0].strip()

        # Phone
        phone = store["phone"]

        # Lat
        lat = store["latitude"]

        # Long
        lon = store["longitude"]
        if not lon:
            lat = "<MISSING>"
            lon = "<MISSING>"

        # Hour
        log.info(page_url)
        req = session.get(page_url, headers=headers)
        if not isinstance(req, SgRequestError):
            req_sel = lxml.html.fromstring(req.text)
            hours = req_sel.xpath('//ul[@class="hours"]/li')
            hours_list = []
            for hour in hours:
                hours_list.append(":".join(hour.xpath("text()")).strip())

            hour = "; ".join(hours_list).strip()

        else:
            page_url = "https://mysagedental.com/find-locations/"
            hour = "<INACCESSIBLE>"

        # Country
        country = "US"

        yield SgRecord(
            locator_domain=website,
            page_url=page_url,
            location_name=location_title,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipcode,
            country_code=country,
            store_number=location_id,
            phone=phone,
            location_type=location_type,
            latitude=lat,
            longitude=lon,
            hours_of_operation=hour,
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
