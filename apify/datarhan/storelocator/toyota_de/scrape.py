from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://kong-proxy-aws.toyota-europe.com/dxp/dealers/api/toyota/de/de/drive/13.38333/52.51667?count=5000&extraCountries=&isCurrentLocation=false"
    domain = "toyota.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
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
                    [" ".join([l for l in e.strip().split()]) for e in hoo if e.strip()]
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
        phone = poi["phone"]
        if phone:
            phone = phone.split("elle")[0].split(",")[0]
        services = [e["service"] for e in poi["services"]]
        services = ", ".join(services) if services else ""
        if not page_url:
            page_url = "https://www.toyota.de/#/publish/my_toyota_my_dealers"

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
            phone=phone,
            location_type=services,
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
