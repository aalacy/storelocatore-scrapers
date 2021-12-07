import json
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "myeyelevel.com"
    start_url = "https://www.myeyelevel.com/US/customer/getCenterList.do"
    country_codes = ["0015", "0014"]
    for code in country_codes:
        formdata = {
            "pageName": "findCenter",
            "centerLati": "",
            "searchType": "",
            "centerLongi": "",
            "surDistance": "",
            "myLocLati": "0",
            "myLocLongi": "0",
            "countryCd": code,
            "cityCd": "",
            "centerName": "",
            "listSort": "D",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)

        for poi in data:
            if poi.get("homeurl"):
                store_url = "https://" + poi["homeurl"]
            else:
                store_url = "<MISSING>"
            if "www.myeyelevel.com" not in store_url:
                continue
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_address = loc_dom.xpath(
                '//ul[@class="copyUl"]//span[@class="link"]/text()'
            )[0]
            structured_adr = parse_address_intl(raw_address)
            location_name = poi["centerName"]
            street_address = structured_adr.street_address_1
            city = structured_adr.city
            if not city and len(raw_address.split(", ")) == 3:
                city = raw_address.split(", ")[1]
            if not city:
                city = loc_dom.xpath('//meta[@name="description"]/@content')[0].replace(
                    "Eye Level ", ""
                )
                if city:
                    street_address = raw_address.split(city)[0].strip()
            state = structured_adr.state
            zip_code = structured_adr.postcode
            store_number = poi["centerNo"]
            phone = poi.get("phone")
            latitude = poi["locLati"]
            longitude = poi["locLongi"]
            hoo = loc_dom.xpath(
                '//ul[descendant::*[contains(text(), "Monday")]]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
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
