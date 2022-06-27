from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("villageinnpizza_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://villageinnpizza.com/locations/"
    locs = []
    with SgRequests(verify_ssl=False) as session:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if (
                'page"><a href="https://villageinnpizza.com/locations/' in line
                and "food-truck" not in line
            ):
                locs.append(line.split('href="')[1].split('"')[0])
        logger.info(("Found %s Locations." % str(len(locs))))
        for loc in locs:
            store = "<MISSING>"
            country = "US"
            logger.info(("Pulling Location %s" % loc))
            website = "villageinnpizza.com"
            typ = "Restaurant"
            r2 = session.get(loc, headers=headers)
            store_sel = lxml.html.fromstring(r2.text)
            city_state_zip = "".join(
                store_sel.xpath(
                    '//div[@class="entry-content-wrapper clearfix"]//div[@itemprop="text"]/p[1]/text()'
                )[-1]
            ).strip()
            city = city_state_zip.split(",")[0]
            state = city_state_zip.split(",")[1].strip().split(" ")[0]
            zc = city_state_zip.split("<")[0].rsplit(" ", 1)[1]
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="entry-content-wrapper clearfix"]//div[@itemprop="text"]/p[3]//text()'
                )
            ).strip()

            hours = (
                "; ".join(
                    store_sel.xpath(
                        '//p[./strong[contains(text(),"Store Hours")]]/text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )

            lines = r2.iter_lines()
            for line2 in lines:
                if "<title>" in line2:
                    name = (
                        line2.split("<title>")[1]
                        .split(" &#8211; Village")[0]
                        .replace("&#8211;", "-")
                    )
                if "]['address']" in line2:
                    add = line2.split('] = "')[1].split('"')[0].strip()
                if "]['long']" in line2:
                    lng = line2.split("] = ")[1].split(";")[0].strip()
                if "]['lat']" in line2:
                    lat = line2.split("] = ")[1].split(";")[0].strip()

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
            )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
