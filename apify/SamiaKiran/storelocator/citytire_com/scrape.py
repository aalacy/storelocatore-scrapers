from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "citytire_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://citytire.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://citytire.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = r.text.split("<div class='col-sm-3 location-item'>")[1:]
        coord_list = soup.findAll("div", {"class": "marker"})
        for loc in loclist:
            loc = loc.split(
                "<a  class='map-toggle' href='#'><i class='fa fa-map-marker'></i></a>"
            )[0]
            loc = BeautifulSoup(loc, "html.parser")
            address = loc.find("p").get_text(separator="|", strip=True).split("|")
            location_name = address[0]
            log.info(location_name)
            raw_address = " ".join(x for x in address[1:])
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            try:
                phone = loc.select_one("a[href*=tel]").text
            except:
                phone = MISSING
            loc = loc.get_text(separator="|", strip=True).split("|")
            if "Sat (Seasonal)" in loc[-1]:
                del loc[-1]
            elif "Sat (Appointment Only)" in loc[-1]:
                del loc[-1]
            elif "Contact your Local Branch" in loc[-1]:
                del loc[-1]
            else:
                hours_of_operation = loc[-1]
            hours_of_operation = loc[-1]
            for coord in coord_list:
                temp = coord.find("strong").text
                if location_name == temp:
                    latitude = coord["data-lat"]
                    longitude = coord["data-lng"]
                    break
            country_code = "CA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
