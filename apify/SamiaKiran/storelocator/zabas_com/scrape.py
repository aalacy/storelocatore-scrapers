from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "zabas_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://zabas.com/restaurant-locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split('"reviewBody":"', 1)[1].split(
            "Interested in owning your own", 1
        )[0]
        loclist = loclist.split("ORDER NOW")
        for loc in loclist[:-1]:
            loc = loc.split("Give us a Review", 1)[0]
            loc = loc.split("\\r\\n")[2:-1]
            location_name = " ".join(x for x in loc[:-2])
            location_name = location_name.replace("&amp;", " ")
            log.info(location_name)
            street_address = loc[-2].replace("&amp;", "")
            phone = loc[-1]
            city = r.text.split('"addressLocality":"', 1)[1].split('"', 1)[0]
            state = r.text.split('"addressRegion":"', 1)[1].split('"', 1)[0]
            yield SgRecord(
                locator_domain="https://zabas.com/",
                page_url="https://zabas.com/restaurant-locations/",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city,
                state=state,
                zip_postal="<MISSING>",
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation="<MISSING>",
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
