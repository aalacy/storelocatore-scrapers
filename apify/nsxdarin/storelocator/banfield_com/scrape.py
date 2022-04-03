from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("banfield_com")
session = SgRequests()
headers = {
    "authority": "www.banfield.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    stores_req = session.get(
        "https://www.banfield.com/locations/hospitals-by-state", headers=headers
    )
    stores_sel = lxml.html.fromstring(stores_req.text)
    locs = stores_sel.xpath('//div[@class="state-hospital-name"]/h4/a/@href')
    for loc in locs:
        page_url = "https://www.banfield.com" + loc
        logger.info(("Pulling Location %s..." % page_url))
        website = "banfield.com"
        typ = "Hospital"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        country = "US"
        lat = ""
        lng = ""
        phone = ""
        store = ""
        zc = ""
        r2 = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(r2.text)

        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines():
            if 'alt="PetSmart-logo"' in line2:
                typ = "Petsmart"
            if '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '"addressRegion":"' in line2:
                state = line2.split('"addressRegion":"')[1].split('"')[0]
            if '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0].strip()
            if '"telephone":"' in line2:
                phone = (
                    line2.split('"telephone":"')[1]
                    .split('"')[0]
                    .replace("+1-", "")
                    .strip()
                )
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
            if '"longitude":"' in line2:
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
            if '"dayOfWeek":"' in line2:
                day = line2.split('"dayOfWeek":"')[1].split('"')[0]
            if '"opens":"' in line2:
                op = line2.split('"opens":"')[1].split('"')[0]
            if '"closes":"' in line2:
                cl = line2.split('"closes":"')[1].split('"')[0]
                if op != cl:
                    hrs = day + ": " + op + "-" + cl
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs

        store = (
            "".join(store_sel.xpath('//div[@class="hospital-id"]/text()'))
            .strip()
            .replace("(#", "")
            .strip()
            .replace(")", "")
            .strip()
        )
        if len(store) <= 0:
            logger.error(page_url)
        add = add.replace("&amp;", "&").replace("amp;", "&")

        yield SgRecord(
            locator_domain=website,
            page_url=page_url,
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
