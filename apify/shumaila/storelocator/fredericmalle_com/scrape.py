from bs4 import BeautifulSoup
import re
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


MISSING = SgRecord.MISSING


def fetch_data():

    cleanr = re.compile(r"<[^>]+>")
    base_url = "https://www.fredericmalle.com"
    url = "https://www.fredericmalle.com/about#/stores/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find_all("div", {"class": "stores__location-wrapper"})
    for loc in loclist:
        title = loc.find("div", {"class": "stores__location-name"}).text
        address = str(loc.findAll("div", {"class": "stores__location-address"})[-1])

        if len(address) < 3:
            address = str(loc.find("div", {"class": "stores__content-content"}))
        address = re.sub(cleanr, " ", address).replace("\n", " ").strip()
        try:
            phone = loc.find("div", {"class": "stores__location-phone"}).text
        except:
            phone = "<MISSING>"
        try:
            hours = loc.find("div", {"class": "stores__location-hours"}).text
        except:
            hours = "<MISSING>"
        try:
            lat, longt = (
                loc.find("a")["href"].split("@", 1)[1].split("data", 1)[0].split(",", 1)
            )
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        pa = parse_address_intl(address)

        street_address = pa.street_address_1
        street = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        pcode = zip_postal.strip() if zip_postal else MISSING

        ccode = pa.postcode
        ccode = ccode.strip() if ccode else MISSING

        yield SgRecord(
            locator_domain=base_url,
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
            raw_address=address,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
