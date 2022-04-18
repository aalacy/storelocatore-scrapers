import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(proxy_country="us", verify_ssl=False)
    domain = "countryfinancial.com"
    start_url = "https://www.countryfinancial.com/services/reps.html"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//ul[@class="plain column-list-two"]/li/a/@href')
    for url in all_states:
        response = session.get(urljoin(start_url, url), headers=hdr)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath("//div[h1]/ul/li/a/@href")
        for url in all_cities:
            response = session.get(urljoin(start_url, url), headers=hdr)
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//p[@class="repaddress"]/a/@href')
            for page_url in all_locations:
                print(page_url)
                loc_response = session.get(page_url, headers=hdr)
                loc_dom = etree.HTML(loc_response.text)
                while not loc_dom:
                    loc_response = session.get(
                        page_url, headers=hdr, proxies=proxies, verify=False
                    )
                    loc_dom = etree.HTML(loc_response.text)
                poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')[1]
                poi = demjson.decode(poi.replace("\n", ""))[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=poi["address"]["streetAddress"],
                    city=poi["address"]["addressLocality"],
                    state=poi["address"]["addressRegion"],
                    zip_postal=poi["address"]["postalCode"],
                    country_code="",
                    store_number="",
                    phone=poi["contactPoint"][0]["telephone"],
                    location_type=poi["@type"],
                    latitude=poi["geo"]["latitude"],
                    longitude=poi["geo"]["longitude"],
                    hours_of_operation="",
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
