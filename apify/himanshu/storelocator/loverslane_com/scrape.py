from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name="loverslane")


def fetch_data():
    base_url = "https://www.loverslane.com"
    r = session.get(base_url + "/stores")
    for link in eval(r.text.split("var stores =")[1].split("];")[0] + "]"):
        lat = link[1]
        lng = link[2]
        name = link[0]
        page_url = base_url + link[-1]
        log.info(page_url)
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        store_sel = lxml.html.fromstring(r1.text)
        address = soup1.find("span", itemprop="streetAddress").text.strip()
        city = soup1.find("span", itemprop="addressLocality").text.strip()
        state = soup1.find("span", itemprop="addressRegion").text.strip()
        zip = soup1.find("span", itemprop="postalCode").text.strip()
        phone = soup1.find("span", itemprop="telephone").text.strip()
        hour = ""
        for hr in soup1.find_all("span", itemprop="openingHours"):
            hour += hr.text + " , "
        hour = hour.rstrip(" , ")
        if len(hour) <= 0:
            hour = ", ".join(
                store_sel.xpath(
                    '//p[./strong[contains(text(),"Store Hours")]]/span/text()'
                )
            ).strip()

        yield SgRecord(
            locator_domain=base_url,
            page_url=page_url,
            location_name=name,
            street_address=address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code="US",
            store_number="<MISSING>",
            phone=phone,
            location_type="loverslane",
            latitude=lat,
            longitude=lng,
            hours_of_operation=hour,
        )


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
