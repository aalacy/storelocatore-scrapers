from lxml import etree
import demjson

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotaoman.com/buyers-support/find-a-showroom/"
    domain = "toyotaoman.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "contactdetails")]/text()')[0]
        .replace("\n", "")
        .replace("\t", "")
        .replace("//", "")
        .replace(";alert(contactdetails);", "")
        .replace("var contactdetails =", "")
    )
    data = demjson.decode(data)

    for i, e in data.items():
        for poi in e:
            location_name = ""
            if location_name and location_name.endswith(","):
                location_name = location_name[:-1]
            raw_address = poi["extaddress"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            city = raw_address.split(", ")[1]
            if "P.C" in city:
                city = raw_address.split(", ")[2]
            phone = (
                etree.HTML(poi["cNumber"]).xpath("//text()")[0].split("/")[0].strip()
            )
            location_type = etree.HTML(poi["serviceoffered"]).xpath("//text()")
            location_type = ", ".join(location_type)
            hoo = etree.HTML(poi["showroomtiming"]).xpath("//text()")[1:]
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
                zip_postal="",
                country_code="Oman",
                store_number="",
                phone=phone,
                location_type=location_type,
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
                raw_address=raw_address,
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
