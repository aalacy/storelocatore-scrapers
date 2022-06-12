import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    # http://en.wikipedia.org/wiki/Extreme_points_of_the_United_Kingdom#Westernmost

    top = 60.850000  # north lat
    left = -8.166667  # west long
    right = 1.766667  # east long
    bottom = 49.85  # south lat

    def uk_borders(latlngs):
        """
        Accepts a list of lat/lng tuples.
        returns the list of tuples that are within the bounding box for the UK.
        """
        inside_box = []
        for (lat, lng) in latlngs:
            if bottom <= lat <= top and left <= lng <= right:
                inside_box.append((lat, lng))
        return inside_box

    # Your scraper here
    session = SgRequests()

    domain = "unode50.com"
    start_url = "https://www.unode50.com/uk/stores#51.494114,-0.255486"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "calendar")]/text()')[0]
    data = json.loads(data)

    for poi in data["*"]["Magento_Ui/js/core/app"]["components"][
        "store-locator-search"
    ]["markers"]:
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        coordinates = [(float(latitude), float(longitude))]
        if not uk_borders(coordinates):
            continue

        store_url = f"https://www.unode50.com/en/int/stores#{latitude},{longitude}"
        location_name = poi["name"]
        if location_name == "g":
            continue
        if "., .," in poi["address"]:
            continue
        raw_address = poi["address"].replace("\n", ", ").replace("\t", ", ").split(", ")
        raw_address = " ".join([elem.strip() for elem in raw_address if elem.strip()])
        addr = parse_address_intl(raw_address)
        city = addr.city
        city = city if city else "<MISSING>"
        street_address = f"{addr.street_address_1} {addr.street_address_2}".replace(
            "None", ""
        ).strip()
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        if not zip_code:
            if len(street_address.split()[-1]) == 3:
                zip_code = " ".join(street_address.split()[-2:])
                street_address = street_address.replace(zip_code, "")
            elif len(street_address.split()[0]) == 3:
                zip_code = " ".join(street_address.split()[:2])
                street_address = street_address.replace(zip_code, "")
        zip_code = zip_code if zip_code else "<MISSING>"
        if len(zip_code.split()[-1]) != 3:
            continue
        country_code = "UK"
        store_number = poi["id"]
        phone = poi["contact_phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
