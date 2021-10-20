import re
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.miniso.com/EN/map"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_countries = dom.xpath('//select[@id="chkcountry"]/option')
    for country in all_countries:
        code = country.xpath("@value")[0]
        country_code = country.xpath(".//text()")[0]
        url = "https://www.miniso.com/EN/map/GetStoreList"
        frm = {
            "chkcountry": code,
            "chkarea": "",
            "k": "",
            "pageindex": "1",
            "pagesize": "500",
        }
        all_locations = session.post(url, data=frm).json()

        for poi in all_locations:
            location_name = poi["StoreName"]
            location_name = location_name if location_name else "<MISSING>"
            addr = parse_address_intl(poi["LinkAddr"])
            street_address = addr.street_address_1
            if addr.street_address_2 and street_address:
                street_address += " " + addr.street_address_2
            elif not street_address and addr.street_address_2:
                street_address = addr.street_address_2
            if not street_address:
                street_address = poi["LinkAddr"].split(", ")[0]
            if not street_address.strip():
                continue
            street_address = street_address.replace("<*B1-143/144/145>", "")
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
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
                raw_address=poi["LinkAddr"],
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
