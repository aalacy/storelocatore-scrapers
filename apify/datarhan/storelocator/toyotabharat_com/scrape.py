from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "toyotabharat.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.post("https://webapi.toyotabharat.com/1.0/api/businessstates")
    dom = etree.XML(response.text)
    all_states = dom.findall("State")
    for state in all_states:
        state_id = state.xpath(".//Id/text()")[0]
        response = session.post(
            f"https://webapi.toyotabharat.com/1.0/api/businessstates/{state_id}/businesscities",
            headers=hdr,
        )
        dom = etree.XML(response.text)
        all_cities = dom.findall("City")
        for city in all_cities:
            city_id = city.xpath(".//Id/text()")[0]
            url = f"https://webapi.toyotabharat.com/1.0/api/dealers/{state_id}/{city_id}/1"
            response = session.post(url)
            dom = etree.XML(response.text)

            all_locations = dom.findall("Dealer")
            for poi_html in all_locations:
                store_number = poi_html.xpath(".//Id/text()")[0]
                location_name = poi_html.xpath(".//Name/text()")[0]
                street_address = poi_html.xpath(".//Address1/text()")[0]
                address_2 = poi_html.xpath(".//Address2/text()")
                if address_2:
                    street_address += " " + address_2[0]
                address_3 = poi_html.xpath(".//Address3/text()")
                if address_3:
                    street_address += " " + address_3[0]
                address_4 = poi_html.xpath(".//Address4/text()")
                if address_4:
                    street_address += " " + address_4[0]
                street_address = street_address.strip()
                if street_address.endswith(","):
                    street_address = street_address[:-1]
                city = poi_html.xpath(".//City/Name/text()")[0]
                state = poi_html.xpath(".//City/State/Name/text()")[0]
                zip_code = poi_html.xpath(".//Pincode/text()")[0]
                country_code = "India"
                page_url = poi_html.xpath(".//URL/text()")[0]
                phone = poi_html.xpath(".//Phone/text()")[0]
                poi_type = poi_html.xpath(".//Facility/Value/text()")[0]
                if "Sales" not in poi_type:
                    continue
                latitude = poi_html.xpath(".//Latitude/text()")[0]
                longitude = poi_html.xpath(".//Longitude/text()")[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
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
