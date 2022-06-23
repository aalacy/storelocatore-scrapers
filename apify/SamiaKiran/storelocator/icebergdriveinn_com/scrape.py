from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "icebergdriveinn_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://icebergdriveinn.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://icebergdriveinn.com/pages/iceberg-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div",
            {"class": "gf_column gf_col-lg-3 gf_col-md-3 gf_col-sm-6 gf_col-xs-12"},
        )
        for loc in loclist:
            location_name = loc.findAll("h3")
            location_name = " ".join(
                x.get_text(separator="|", strip=True).replace("|", " ")
                for x in location_name
            )
            location_name = location_name.replace("(Shake Shop Location)", "")
            if not location_name:
                continue
            log.info(location_name)
            temp = loc.findAll("p")
            if "Monday" in loc.text:
                address = temp[0].text.split("(")
                try:
                    phone = "(" + address[1]
                except:
                    phone = temp[1].text
                raw_address = address[0]
                hours_of_operation = " ".join(
                    x.get_text(separator="|", strip=True).replace("|", " ")
                    for x in temp[1:]
                )
                hours_of_operation = hours_of_operation.replace(phone, "").replace(
                    "Delivery through Door Dash", ""
                )
            else:
                address = temp[0].text + " " + temp[1].text
                phone = temp[-1].text
                hours_of_operation = MISSING
                phone = phone.replace("Delivery through DoorDash", "")
                raw_address = address.replace(",", " ").replace(
                    "99Fillmore", "99 Fillmore"
                )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "US"
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
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
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
