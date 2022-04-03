from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sglogging import sglog
from sgscrape.sgpostal import parse_address_usa
from sgscrape.sgrecord_deduper import SgRecordDeduper

DOMAIN = "dontdrivedirty.com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data(sgw: SgWriter):

    api_url = "https://dontdrivedirty.com/locationsandpricing/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    geos = []
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "single")]')
    for d in div:
        page_url = "".join(d.xpath('.//a[text()="See Details"]/@href'))
        if "18323" in page_url:
            continue
        log.info("Page => " + page_url)
        location_name = (
            "".join(d.xpath('.//p[@class="h5 mb-2"]/strong/text()'))
            .split("-")[0]
            .strip()
        )
        raw_address = (
            " ".join(d.xpath('.//strong[text()="Address: "]/following-sibling::text()'))
            .replace("\n", "")
            .strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        latitude, longitude = "", ""
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "lat:")]/text()'))
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "lat:")]/text()'))
                .split("lng:")[1]
                .split("}")[0]
                .strip()
            )
        except:
            latitude, longitude = "", ""

        hours_of_operation = (
            " ".join(d.xpath('.//strong[text()="Hours: "]/following-sibling::text()'))
            .replace("\n", "")
            .strip()
        )

        location_type = "Open"
        if "-" in hours_of_operation.strip()[0:4]:
            hours_of_operation = MISSING
            location_type = "Coming Soon"

        if "TEMPORARILY CLOSED" in location_name:
            location_name = location_name.split("–")[0].strip()
            location_type = "TEMPORARILY CLOSED".title()

        try:
            if not latitude:
                map_link = tree.xpath('.//a[@class="btn"]')[0].xpath("@href")[0]
                latitude = map_link.split("@")[1].split(",")[0]
                longitude = map_link.split("@")[1].split(",")[1].split(",")[0]

            if "data" in latitude:
                latitude = r.text.split("lat: ", 1)[1].split(",")[0].strip()
                longitude = r.text.split("lng: ", 1)[1].split("}")[0].strip()

            if latitude + longitude in geos:
                latitude = ""
                longitude = ""
            else:
                geos.append(latitude + longitude)
        except:
            latitude = MISSING
            longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        row = SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
