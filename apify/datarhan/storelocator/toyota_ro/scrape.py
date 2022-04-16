from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_urls = [
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/xk/sq/drive/20.953599/42.6430165?count=500&extraCountries=SQ&limitSearchDistance=0&isCurrentLocation=false&services=",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/ro/ro/drive/26.08333/44.4?count=500&extraCountries=&isCurrentLocation=false",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/ch/de/drive/7.43861/46.95083?count=500&extraCountries=li&isCurrentLocation=false",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/se/sv/drive/13.167381/55.701493?count=500&extraCountries=&limitSearchDistance=0&isCurrentLocation=false&services=",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/sk/sk/drive/17.135763/48.156086?count=500&extraCountries=&limitSearchDistance=60&isCurrentLocation=false",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/dk/da/drive/12.079135/55.648779?count=500&extraCountries=&isCurrentLocation=false",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/gb/en/drive/-0.081018/51.652085?count=500&extraCountries=&isCurrentLocation=false",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/es/es/drive/-3.703583/40.416705?count=500&extraCountries=&isCurrentLocation=false",
        "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/fi/fi/drive/22.75/60.5?count=500&extraCountries=&isCurrentLocation=false",
        "https://kong-prox-aws.toyota-europe.com/dxp/dealers/api/toyota/fr/fr/drive/0.428551/44.064432?count=500&extraCountries=MC&isCurrentLocation=false",
    ]
    domain = "toyota.ro"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for url in start_urls:
        data = session.get(url, headers=hdr).json()
        for poi in data["dealers"]:
            page_url = poi.get("url")
            hoo = ""
            if page_url:
                loc_response = session.get(page_url, headers=hdr)
                if loc_response.status_code == 200:
                    loc_dom = etree.HTML(loc_response.text)

                    hoo = loc_dom.xpath(
                        '//div[h3[i[@class="fa fa-clock-o fa-fw"]]]/following-sibling::div[1]//text()'
                    )
                    hoo = " ".join(
                        [
                            " ".join([l for l in e.strip().split()])
                            for e in hoo
                            if e.strip()
                        ]
                    )
                    if hoo == "-":
                        hoo = ""
                    hoo = hoo.replace("<o:p></o:p>", "")
            street_address = poi["address"]["address1"]
            city = poi["address"]["city"]
            zip_code = poi["address"]["zip"]
            street_address = street_address.split(zip_code)[0]
            if street_address.endswith(","):
                street_address = street_address[:-1]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=city,
                state=poi["address"]["region"],
                zip_postal=zip_code,
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
