import re
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

log = sglog.SgLogSetup().get_logger(logger_name="seasons52.com")
session = SgRequests()
headers = {
    "authority": "www.seasons52.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


headers1 = {
    "authority": "www.eddiev.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


def fetch_data():

    cleanr = re.compile(r"<[^>]+>")

    url = "https://www.seasons52.com/locations/all-locations"
    stores_req = session.get(url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@id="locDetailsId"]/@href')
    stores.append("/locations/nj/paramus/paramus/4556")
    for store_url in stores:
        page_url = "https://www.seasons52.com" + store_url
        store = page_url.split("/")[-1]
        url = "https://www.seasons52.com/ajax/headerlocation.jsp?restNum=" + str(store)
        log.info(url)
        loc = (
            session.get(url, headers=headers1).text.replace('"', "").strip().split(",")
        )
        title = loc[1]
        lat, longt = loc[2].split("*", 1)
        street = loc[3]
        city = loc[4]
        state = loc[5]
        pcode = loc[6]
        phone = loc[7]
        hours = re.sub(cleanr, "", loc[8]).strip()
        yield SgRecord(
            locator_domain="https://www.seasons52.com/",
            page_url=page_url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
