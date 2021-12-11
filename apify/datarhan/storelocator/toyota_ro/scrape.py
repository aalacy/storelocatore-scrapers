from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/xk/sq/drive/20.953599/42.6430165?count=500&extraCountries=SQ&limitSearchDistance=0&isCurrentLocation=false&services=",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/ro/ro/drive/26.08333/44.4?count=500&extraCountries=&isCurrentLocation=false",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/ch/de/drive/7.43861/46.95083?count=500&extraCountries=li&isCurrentLocation=false",
    ]
    domain = "toyota.ro"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for url in start_urls:
        data = session.get(url, headers=hdr).json()
        for poi in data["dealers"]:
            page_url = poi["url"]
            loc_response = session.get(page_url)
            hoo = ""
            if loc_response.status_code == 200:
                loc_dom = etree.HTML(loc_response.text)

                hoo = loc_dom.xpath(
                    '//div[h3[i[@class="fa fa-clock-o fa-fw"]]]/following-sibling::div[1]//text()'
                )
                hoo = " ".join(
                    [" ".join([l for l in e.strip().split()]) for e in hoo if e.strip()]
                )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"]["address1"],
                city=poi["address"]["city"],
                state=poi["address"]["region"],
                zip_postal=poi["address"]["zip"],
                country_code=poi["country"],
                store_number=poi.get("localDealerID"),
                phone=poi["phone"],
                location_type="",
                latitude=poi["address"]["geo"]["lat"],
                longitude=poi["address"]["geo"]["lon"],
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
