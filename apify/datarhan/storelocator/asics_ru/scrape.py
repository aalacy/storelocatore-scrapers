from w3lib.url import add_or_replace_parameter
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://www.asics.com/in/en-in/store-locator.json?default=y",
        "https://www.asics.com/my/en-my/store-locator.json?default=y",
        "https://www.asics.com/ru/ru-ru/store-locator.json?default=y&page=1",
        "https://www.asics.com/sg/en-sg/store-locator.json?default=y",
        "https://www.asics.com/th/en-th/store-locator.json?default=y",
        "https://www.asics.com/za/en-za/store-locator.json?default=y",
    ]
    domain = "asics.ru"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for url in start_urls:
        data = session.get(url, headers=hdr).json()
        all_locations = list(data["Stores"].values())
        next_page = data["HasNext"]
        while next_page:
            data = session.get(
                add_or_replace_parameter(url, "page", data["Next"]), headers=hdr
            ).json()
            all_locations += list(data["Stores"].values())
            next_page = data["HasNext"]

        for poi in all_locations:
            page_url = urljoin(url, poi["URL"])
            street_address = poi["Address"]
            if street_address.endswith(","):
                street_address = street_address[:-1]
            city = poi["City"]
            zip_code = poi["Postcode"]
            if "ru-ru" in url:
                if street_address.split(",")[0].isdigit():
                    zip_code = street_address.split(",")[0]
                    city = street_address.split(",")[1]
                    street_address = ", ".join(street_address.split(",")[2:])
                else:
                    city = street_address.split(",")[0]
                    street_address = ", ".join(street_address.split(",")[1:])
            location_type = poi["StoreType"]
            if location_type != "brandstore":
                continue

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["Title"],
                street_address=street_address,
                city=city,
                state=poi["Region"],
                zip_postal=zip_code,
                country_code=poi["URL"].split("/")[1].upper(),
                store_number=poi["ID"],
                phone=poi["Phone"],
                location_type=location_type,
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
                hours_of_operation="",
                raw_address=poi["Address"],
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
