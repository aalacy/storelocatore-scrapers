from lxml import html

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "icebreaker.com"
    start_url = "https://hosted.where2getit.com/icebreaker/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E6F5D49F0-91F8-11E0-89D3-C9B5E425BB5D%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E250%3C%2Flimit%3E%3Corder%3Erank%2C+_distance%3C%2Forder%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E%3C%2Faddressline%3E%3Clongitude%3E{}%3C%2Flongitude%3E%3Clatitude%3E{}%3C%2Flatitude%3E%3Ccountry%3E%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E200%3C%2Fsearchradius%3E%3Cradiusuom%3Emile%3C%2Fradiusuom%3E%3Cwhere%3E%3Cactive%3E%3Ceq%3E1%3C%2Feq%3E%3C%2Factive%3E%3Cor%3E%3Cicebreakertouchlab%3E%3Ceq%3EYes%3C%2Feq%3E%3C%2Ficebreakertouchlab%3E%3Cicebreakeroutlet%3E%3Ceq%3EYes%3C%2Feq%3E%3C%2Ficebreakeroutlet%3E%3Cpremiumretailers%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpremiumretailers%3E%3Cgeneralretailers%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgeneralretailers%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.BRITAIN,
        ],
        max_search_distance_miles=100,
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lng, lat), headers=hdr)
        dom = html.fromstring(bytes(response.text, encoding="utf8"))

        all_locations = dom.xpath("//poi")
        for poi_html in all_locations:
            page_url = "https://www.icebreaker.com/en-us/stores"
            location_name = poi_html.xpath(".//name/text()")
            location_name = location_name[0] if location_name else ""
            street_address = poi_html.xpath(".//address1/text()")
            street_address = street_address[0] if street_address else ""
            city = poi_html.xpath(".//city/text()")
            city = city[0] if city else ""
            state = poi_html.xpath(".//state/text()")
            state = state[0] if state else ""
            zip_code = poi_html.xpath(".//postalcode/text()")
            zip_code = zip_code[0] if zip_code else ""
            country_code = poi_html.xpath(".//country/text()")
            country_code = country_code[0] if country_code else ""
            phone = poi_html.xpath(".//phone/text()")
            phone = phone[0] if phone else ""
            latitude = poi_html.xpath(".//latitude/text()")
            latitude = latitude[0] if latitude else ""
            longitude = poi_html.xpath(".//longitude/text()")
            longitude = longitude[0] if longitude else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
