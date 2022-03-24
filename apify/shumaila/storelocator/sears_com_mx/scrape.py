from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

MISSING = SgRecord.MISSING


def fetch_data():

    url = "https://resources.sears.com.mx/medios-plazavip/swift/v1/Sears/assets/js/scriptSucursalesSears7_6.js"
    r = session.get(url, headers=headers)
    divlist = r.text.split("<option")[1:]

    for div in divlist:
        div = "<option" + div.split("</option", 1)[0] + "</option>"
        soup = BeautifulSoup(div, "html.parser").find("option")
        longt, lat = (
            soup["data-url"].split("!2d", 1)[1].split("!2m", 1)[0].split("!3d", 1)
        )

        try:
            lat = lat.split("!", 1)[0]
        except:
            pass
        store = soup["data-tienda"]
        title = soup.text.strip()

        content = soup["data-text"]
        address, phone = content.split("Tel. ", 1)
        address = address.replace("|", "").strip()
        phone, hours = phone.split("|", 1)
        raw_address = address.replace("\n", " ").strip()
        pa = parse_address_intl(raw_address)
        street_address = pa.street_address_1
        street = street_address if street_address else MISSING
        city = pa.city
        city = city.strip() if city else MISSING
        state = pa.state
        state = state.strip() if state else MISSING
        zip_postal = pa.postcode
        pcode = zip_postal.strip() if zip_postal else MISSING
        yield SgRecord(
            locator_domain="https://www.sears.com.mx/",
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="MX",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours.strip(),
            raw_address=raw_address,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
