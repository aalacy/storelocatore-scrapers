from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "pigglywiggly_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "http://www.pigglywiggly.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "http://www.pigglywiggly.com/store-locations"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        states = soup.findAll("span", {"class": "field-content"})
        for statelink in states:
            statelink = "http://www.pigglywiggly.com" + statelink.find("a")["href"]
            stores_req = session.get(statelink, headers=headers)
            bs = BeautifulSoup(stores_req.text, "html.parser")
            street = bs.findAll("div", {"class": "street-address"})
            state = bs.findAll("span", {"class": "region"})
            city = bs.findAll("span", {"class": "locality"})
            pcode = bs.findAll("span", {"class": "postal-code"})
            country = bs.findAll("div", {"class": "country-name"})
            phone = bs.findAll("div", {"class": "views-field-field-phone-value"})
            location = bs.findAll("div", {"class": "location map-link"})
            for st, cit, ste, pc, cty, ph, loc in zip(
                street, city, state, pcode, country, phone, location
            ):
                street = st.text.strip()
                city = cit.text.strip()
                state = ste.text.strip()
                pcode = pc.text.strip()
                country = cty.text.strip()
                phone = ph.find("span").text.strip()
                coords = loc.find("a")["href"]
                coords = coords.split("q=")[1].split("+%")[0].strip()
                lat = coords.split("+")[0].strip()
                lng = coords.split("+")[1].strip()
                if country == "Unites States":
                    country = "US"

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=statelink,
                    location_name="Piggly Wiggly",
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code=country.strip(),
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=MISSING,
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
