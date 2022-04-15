from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "jaguarusa.com"

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    start_url = (
        "https://www.jaguarusa.com/retailer-locator/index.html?region={}&filter=dealer"
    )
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    for code in states:
        response = session.get(start_url.format(code), headers=hdr)
        dom = etree.HTML(response.text)

        all_poi_html = dom.xpath('//div[@class="infoCardDealer infoCard"]')
        for poi_html in all_poi_html:
            location_name = poi_html.xpath(
                './/span[@class="dealerNameText fontBodyCopyLarge"]/text()'
            )
            location_name = location_name[0] if location_name else ""
            street_address_raw = poi_html.xpath('.//span[@class="addressText"]/text()')[
                0
            ]
            street_address = street_address_raw.split(",")[0]
            street_address = street_address if street_address else ""
            city = street_address_raw.split(",")[1].strip()
            state = street_address_raw.split(",")[2].strip()
            zip_code = street_address_raw.split(",")[3].strip()
            store_number = poi_html.xpath("@data-ci-code")[0]
            phone = poi_html.xpath('.//a[@class="itemMobileInner"]/text()')
            phone = phone[0] if phone else ""
            latitude = poi_html.xpath("@data-lat")[0]
            latitude = latitude if latitude else ""
            longitude = poi_html.xpath("@data-lng")[0]
            longitude = longitude if longitude else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url.format(code),
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
                hours_of_operation="",
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
