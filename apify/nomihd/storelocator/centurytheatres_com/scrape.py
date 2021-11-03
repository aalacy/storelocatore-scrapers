from sgrequests import SgRequests
import json
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "centurytheatres"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def fetch_data():
    r = session.get("https://cinemark.com/full-theatre-list")

    stores_sel = lxml.html.fromstring(r.text)
    links = stores_sel.xpath('//div[@class="columnList wide"]//a/@href')
    for link in links:
        page_url = "https://cinemark.com/" + link
        log.info(page_url)
        r1 = session.get(page_url)
        store_sel = lxml.html.fromstring(r1.text)
        info = "".join(
            store_sel.xpath('//script[@type="application/ld+json"]/text()')
        ).strip()

        try:
            data = json.loads(info)
            for address in data["address"]:
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zipp = address["postalCode"]
                country_code = address["addressCountry"]
            phone = data["telephone"]
            location_name = data["name"]
            if "NOW CLOSED".lower() in location_name.lower():
                continue
            location_type = data["@type"]
            latitude = (
                "".join(store_sel.xpath('//div[@class="theatreMap"]/a/img/@data-src'))
                .split("pp=")[1]
                .split(",")[0]
            )
            longitude = (
                "".join(store_sel.xpath('//div[@class="theatreMap"]/a/img/@data-src'))
                .split("pp=")[1]
                .split(",")[1]
                .split("&")[0]
            )

            yield SgRecord(
                locator_domain=website,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number="<MISSING>",
                phone=phone if phone else "<MISSING>",
                location_type=location_type,
                latitude=latitude if latitude else "<MISSING>",
                longitude=longitude if longitude else "<MISSING>",
                hours_of_operation="<MISSING>",
            )

        except:
            pass


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
