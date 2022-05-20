from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

session = SgRequests()
website = "dentalservice_net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://locations.dentalservice.net/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        locations = []
        search_url = "https://locations.dentalservice.net/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        children = soup.findAll("li", {"class": "location-link"})
        for child in children:
            links = child.findAll("a")
            for link in links:
                url = link["href"]
                if url.find("locations.") != -1:
                    locations.append(url)
                    if url.find("/college-station") != -1:
                        locations.pop(-1)
                    elif url.find("/cypress-dentures") != -1:
                        locations.pop(-1)
                    elif url.find("/denison") != -1:
                        locations.pop(-1)
                    elif url.find("/euless") != -1:
                        locations.pop(-1)
                    elif url.find("/georgetown") != -1:
                        locations.pop(-1)
                    elif url.find("/granbury") != -1:
                        locations.pop(-1)
                    elif url.find("/greenville") != -1:
                        locations.pop(-1)
                    elif url.find("/humble") != -1:
                        locations.pop(-1)
                    elif url.find("/kyle") != -1:
                        locations.pop(-1)
                    elif url.find("/lake-worth") != -1:
                        locations.pop(-1)
                    elif url.find("/pearland") != -1:
                        locations.pop(-1)
                    elif url.find("/schertz") != -1:
                        locations.pop(-1)
                    elif url.find("/waxahachie") != -1:
                        locations.pop(-1)
                    elif url.find("/paducah") != -1:
                        locations.pop(-1)
                    elif url.find("slidell-dentures") != -1:
                        locations.pop(-1)
                    elif url.find("norman-ok-dentures") != -1:
                        locations.pop(-1)
                    elif url.find("arlington") != -1:
                        locations.pop(-1)
                    elif url.find("clarksville-dentures") != -1:
                        locations.pop(-1)
                    elif url.find("smyrna-dentures") != -1:
                        locations.pop(-1)
                    elif url.find("spring-hill") != -1:
                        locations.pop(-1)
                    elif url.find("katy") != -1:
                        locations.pop(-1)
        for loc in locations:
            stores_req = session.get(loc, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            info = soup.find("script", {"type": "application/ld+json"})
            info = str(info)
            info = info.rstrip("</script>").strip()
            info = info.lstrip('<script type="application/ld+json">').strip()
            info = json.loads(info)
            url = loc
            title = info["name"]
            phone = info["telephone"]
            street = info["address"]["streetAddress"]
            city = info["address"]["addressLocality"]
            state = info["address"]["addressRegion"]
            pcode = info["address"]["postalCode"]
            infotext = str(info)
            if infotext.find("areaServed") != -1:
                lat = info["areaServed"]["geoMidpoint"]["latitude"]
                lng = info["areaServed"]["geoMidpoint"]["longitude"]
            else:
                lat = info["geo"]["latitude"]
                lng = info["geo"]["longitude"]
            hoo = ""
            if infotext.find("openingHoursSpecification") != -1:
                hours = info["openingHoursSpecification"]
                for hr in hours:
                    day = hr["dayOfWeek"]
                    opens = hr["opens"]
                    closes = hr["closes"]
                    hrs = day + " " + opens + " " + closes
                    hoo = hoo + ", " + hrs
            else:
                hours = info["openingHours"]
                for hr in hours:
                    hrs = hr
                    hrs = hrs.replace("Mo", "Monday")
                    hrs = hrs.replace("Tu", "Tuesday")
                    hrs = hrs.replace("We", "Wednesday")
                    hrs = hrs.replace("Th", "Thursday")
                    hrs = hrs.replace("Fr", "Friday")
                    hoo = hoo + ", " + hrs
            hoo = hoo.lstrip(",")
            hoo = hoo.strip()
            if title.find("Affordable") == -1:
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=loc,
                    location_name=title.strip(),
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=SgRecord.MISSING,
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hoo.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE},
                fail_on_empty_id=True,
            )
            .with_truncate(SgRecord.Headers.LATITUDE, 3)
            .with_truncate(SgRecord.Headers.LONGITUDE, 3)
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
