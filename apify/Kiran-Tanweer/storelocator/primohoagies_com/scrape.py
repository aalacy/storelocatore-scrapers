from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser
import os

os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"
session = SgRequests()
website = "floridatile_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
headers2 = {
    'authority': 'in.getclicky.com',
    'method': 'POST',
    'path': '/in.php?site_id=101187675&type=ping&jsuid=2412129655&hmset&mime=js&x=0.46474500551401476',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'content-length': '100000',
    'content-type': 'text/plain;charset=UTF-8',
    'cookie': 'cluid=2412129655',
    'origin': 'https://www.floridatile.com',
    'referer': 'https://www.floridatile.com/',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    }

DOMAIN = "https://www.floridatile.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.primohoagies.com/sitemap.php"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        locations = soup.findAll("ul", {"class": "list"})[1].findAll('a')
        for loc in locations:
            title = loc.text
            link = loc['href']
            stores_req = session.get(link, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            details = soup.findAll("div", {"class": "row"})[1]
            address = details.find("div", {"class":"p-street-address"})
            if address is not None:
                street = address.find('span', {'itemprop':'streetAddress'}).text
                city = address.find('span', {'itemprop':'addressLocality'}).text
                state = address.find('span', {'itemprop':'addressRegion'}).text
                pcode = address.find('span', {'itemprop':'postalCode'}).text
                lat = soup.find("meta", {"itemprop":"latitude"})['content']
                lng = soup.find("meta", {"itemprop":"longitude"})['content']
                phone = details.find("h4", {"itemprop":"telephone"}).text
                hours = details.find("div", {"class":"hours"}).text
                hours = hours.replace('day', 'day ')
                hours = hours.replace('pm', 'pm ')
                hours = hours.strip()
                street = street.replace('\n', ' ').strip()

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code="US",
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

##fetch_data()
