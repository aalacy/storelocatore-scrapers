from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape import sgpostal as parser
import os


os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"


session = SgRequests()
website = "elietahari_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.elietahari.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://cdn.shopify.com/s/files/1/0350/8997/3385/t/49/assets/ndnapps-geojson.js?v=12382587392219603945"
        stores_req = session.get(search_url, headers=headers)
        soup = stores_req.text
        r_text = soup.split("eqfeed_callback(")[1].split(")")[0]
        locations = r_text.split("}},")
        link = "https://www.elietahari.com/pages/store-locator"
        r = session.get(link, headers=headers)
        bs = BeautifulSoup(r.text, "html.parser")
        hours = bs.findAll("div", {"class": "hours"})
        for locs, hr in zip(locations, hours):
            hoo = hr.text
            hoo = hoo.replace("\n", " ")
            hoo = hoo.replace("Opens", "")
            hoo = hoo.replace("Hours", "")
            hoo = hoo.replace("  ", " ")
            hoo = hoo.strip()
            title = locs.split('name:"')[1].split('",')[0]
            address = locs.split(',address:"')[1].split('",')[0]
            phone = locs.split("phone")[1].split(",")[0]
            phone = phone.strip(":").strip()
            phone = phone.strip('"').strip()
            if phone == "null":
                phone = "<MISSING>"
            storeid = locs.split(",id:")[1].split(",")[0]

            url = "https://www.elietahari.com" + locs.split('url:"')[1].split('",')[0]
            url = url.replace("\\", "")
            lat = locs.split('lat:"')[1].split('",')[0]
            lng = locs.split('lng:"')[1].split('",')[0]
            if (
                url
                == "https://www.elietahari.com/apps/store-locator/elie-tahari-pembroke-gardens.html"
            ):
                phone = "954-589-1399"
            address = address.rstrip(", United States")
            parsed = parser.parse_address_intl(address)
            street1 = (
                parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
            )
            street = (
                (street1 + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else street1
            )
            city = parsed.city if parsed.city else "<MISSING>"
            state = parsed.state if parsed.state else "<MISSING>"
            pcode = parsed.postcode if parsed.postcode else "<MISSING>"
            country = "US"

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state,
                zip_postal=pcode,
                country_code=country,
                store_number=storeid,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hoo,
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
