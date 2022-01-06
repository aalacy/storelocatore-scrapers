import json

from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "kumon.com"
    hdr = {
        "authority": "www.kumon.com",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://www.kumon.com",
        "referer": "https://www.kumon.com/locations",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    countries = [SearchableCountries.USA, SearchableCountries.CANADA]
    for country in countries:
        all_coordinates = DynamicGeoSearch(
            country_codes=[country],
            expected_search_radius_miles=50,
        )
        start_url = (
            "https://www.kumon.com/Services/KumonWebService.asmx/GetCenterListByRadius"
        )

        for coord in all_coordinates:
            lat, lng = coord
            if country == SearchableCountries.USA:
                country_code = "USA"
            else:
                country_code = "CANADA"
            frm = {
                "countryCode": country_code,
                "distanceUnit": "mi",
                "latitude": lat,
                "longitude": lng,
                "radius": 50,
                "searchAddress": "",
                "showVirtualFlg": 0,
            }
            response = session.post(start_url, json=frm, headers=hdr)
            data = json.loads(response.text)

            all_poi = data["d"]
            for poi in all_poi:
                page_url = "https://www.kumon.com/{}".format(poi["EpageUrl"])
                if page_url == "https://www.kumon.com/":
                    continue
                location_name = poi["CenterName"]
                street_address = poi["Address"]
                if poi.get("Address2"):
                    street_address += ", " + poi["Address2"]
                if poi.get("Address3"):
                    street_address += " " + poi["Address3"]
                city = poi["City"]
                state = poi["StateCode"]
                zip_code = poi["ZipCode"]
                country_code = poi["Country"]
                store_number = poi["K2CenterID"]
                phone = poi["Phone"]
                if phone and phone.startswith("-"):
                    phone = phone[1:]
                latitude = poi["Lat"]
                longitude = poi["Lng"]

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
                    location_type=SgRecord.MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
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
