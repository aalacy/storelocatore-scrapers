import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/8635/stores.js?callback=SMcallback2"
    domain = "loversstores.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr)
    data = json.loads(data.text.split("SMcallback2(")[-1][:-1])
    for poi in data["stores"]:
        raw_address = poi["address"].split("<br/>")
        if len(raw_address) == 1:
            raw_address = poi["address"].split("<br>")
        if len(raw_address[-1].split(", ")) == 3:
            raw_address = [raw_address[0]] + [
                raw_address[-1].split(", ")[0]
                + ", "
                + " ".join(raw_address[-1].split(", ")[1:])
            ]
        hoo = etree.HTML(poi["description"]).xpath("//text()")[1:]
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("Curbside")[0].strip()
        location_type = ""
        if not hoo:
            location_type = "temporary closed"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://loversstores.com/pages/store_locator",
            location_name=poi["name"],
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1].split()[0],
            zip_postal=raw_address[1].split(", ")[-1].split()[-1],
            country_code="",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type=location_type,
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
