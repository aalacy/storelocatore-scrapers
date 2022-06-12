import csv
import json
import codecs
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.drmartens.com/uk/en_gb/store-finder?q={}&page=0"
    domain = "drmartens.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    url = "https://pkgstore.datahub.io/core/world-cities/world-cities_csv/data/6cc66692f0e82b18216a48443b6b95da/world-cities_csv.csv"
    response = session.get(url)
    all_cities = csv.reader(
        codecs.iterdecode(response.iter_lines(), "utf-8"), delimiter=","
    )
    for city in all_cities:
        if city[0] == "name":
            continue
        url = start_url.format(city[0].lower().replace(" ", "%20"))
        response = session.get(url)
        try:
            data = json.loads(response.text)
        except Exception:
            continue
        all_locations = data["data"]
        total = data["total"]
        if total > 10:
            pages = total // 10 + 1
            for p in range(1, pages):
                data = session.get(
                    add_or_replace_parameter(url, "page", str(p)), headers=hdr
                )
                if not response.text:
                    continue
                data = json.loads(response.text)
                all_locations += data["data"]

        for poi in all_locations:
            street_address = poi["line1"]
            if poi["line2"]:
                street_address += " " + poi["line2"]
            addr = parse_address_intl(f'{poi["town"]} {poi["postalCode"]}')
            city_name = addr.city
            state = addr.state
            zip_code = addr.postcode
            hoo = []
            if poi.get("openings"):
                for day, hours in poi["openings"].items():
                    hoo.append(f"{day} {hours}")
            hoo = " ".join(hoo) if hoo else ""
            country_code = SgRecord.MISSING

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.drmartens.com/us/en/store-finder",
                location_name=poi["displayName"],
                street_address=street_address,
                city=city_name,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=poi["phone"].split(":")[-1].strip(),
                location_type=SgRecord.MISSING,
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


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
