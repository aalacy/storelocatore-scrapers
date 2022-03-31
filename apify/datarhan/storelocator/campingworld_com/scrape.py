from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "campingworld.com"
    start_url = "https://rv.campingworld.com/dealersinradius?miles=400&lat={}&lon={}&locationsearch=true"

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=250
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng))
        if response.status_code != 200:
            continue
        all_codes = response.text[1:-1]

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "cookie": f"liveagent_oref=https://www.campingworld.com/; liveagent_vc=4; cw_searchLat={lat}; cw_searchLon={lng}; cw_searchDealers={all_codes}",
        }

        url = "https://rv.campingworld.com/api/locationcards"
        params = {
            "limit": "1000",
            "miles": "400",
            "glcodes": "all_codes",
            "lat": lat,
            "lon": lng,
            "locationsearch": False,
            "service": False,
            "locationPage": True,
        }
        data = session.get(url, params=params, headers=headers).json()
        all_locations = data["locations"]

        for poi in all_locations:
            base_url = "https://rv.ganderoutdoors.com/dealer/"
            page_url = urljoin(base_url, poi["dealer_url"])
            location_name = poi["marketingname"]
            street_address = poi["billing_street"]
            city = poi["billing_city"]
            state = poi["statecode"]
            zip_code = poi["billing_zip"]
            phone = poi["phonenumber"]
            latitude = poi["lat"]
            longitude = poi["lon"]
            if poi.get("store_hours_mf_open"):
                mf_open = poi["store_hours_mf_open"]
                mf_close = poi["store_hours_mf_closed"]
                sat_open = poi["store_hours_sat_open"]
                sat_close = poi["store_hours_sat_closed"]
                sun_open = poi["store_hours_sun_open"]
                sun_close = poi["store_hours_sun_closed"]
                hoo = f"Mon-Fri: {mf_open} - {mf_close} Sat: {sat_open} - {sat_close} Sun: {sun_open} - {sun_close}"
            else:
                hdr = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
                }
                loc_response = session.get(page_url, headers=hdr)
                if loc_response.status_code != 200:
                    hoo = ""
                else:
                    loc_dom = etree.HTML(loc_response.text)
                    hoo = loc_dom.xpath(
                        '//div[@id="dealerHours"]/div[1]/div/div/text()'
                    )
                    hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number="",
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
