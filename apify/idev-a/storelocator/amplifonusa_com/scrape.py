from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.amplifonusa.com",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://www.amplifonusa.com/our-program/clinic-locator/search-results-page?addr=&lat=44.062311&long=-72.74364",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def header1(lat, lng):
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Host": "pnapi.invoca.net",
        "Referer": f"https://www.amplifonusa.com/our-program/clinic-locator/search-results-page?addr=&lat={lat}&long={lng}",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


logger = SgLogSetup().get_logger("amplifonusa")

locator_domain = "https://www.amplifonusa.com"
base_url = "https://www.amplifonusa.com/our-program/clinic-locator/search-results-page.ahhcgetStores.json?addr=&lat={}&long={}"
json_url = "https://pnapi.invoca.net/1686/na.jsonp?"


def fetch_data(search):
    for lat, lng in search:
        with SgRequests(proxy_country="us") as http:
            data = {
                "countryCode": "US",
                "latitude": str(lat),
                "longitude": str(lng),
                "locale": "en_US",
                "limit": "200",
                "radius": "200000",
                "networks": "",
                "subnetworks": "",
                "maxNumResults": "200",
                "type": "",
            }
            try:
                locations = http.post(
                    base_url.format(lat, lng), headers=_headers, data=data
                ).json()
            except:
                continue
            logger.info(f"[{lat, lng}] {len(locations)}")
            if locations:
                search.found_location_at(lat, lng)
            for _ in locations:
                phone = ""
                url = f"https://pnapi.invoca.net/1686/na.jsonp?network_id=1686&js_version=4.25.0&tag_id=1686%2F3823703601&request_data_shared_params=%7B%22calling_page%22%3A%22https%3A%2F%2Fwww.amplifonusa.com%2Four-program%2Fclinic-locator%2Fsearch-results-page%3Faddr%3D%26lat%3D{lat}%26long%3D{lng}%22%2C%22customer_journey%22%3A%22%2Four-program%2Fclinic-locator%2Fsearch-results-page%22%2C%22adobe_id%22%3A%2262252471091252517892297644018594141752%22%2C%22utm_medium%22%3A%22direct%22%2C%22utm_source%22%3A%22direct%22%2C%22invoca_id%22%3A%22i-58d53216-3d55-48c3-f4b7-6eafd324080c%22%2C%22inv_campaign_channel%22%3A%22other%22%2C%22inv_campaign_full%22%3A%22other%22%2C%22hhpCode%22%3A%22N%2FA%22%2C%22hhpName%22%3A%22N%2FA%22%2C%22gcm_uid%22%3Anull%2C%22business_unit%22%3Anull%2C%22channel%22%3Anull%2C%22CountryCode%22%3Anull%2C%22dealer%22%3Anull%2C%22format%22%3Anull%2C%22gclid%22%3Anull%2C%22gclsrc%22%3Anull%2C%22id%22%3Anull%2C%22inv_local_national%22%3Anull%2C%22keywordterm%22%3Anull%2C%22leadtype_destination_number%22%3Anull%2C%22mci%22%3Anull%2C%22msclkid%22%3Anull%2C%22name%22%3Anull%2C%22static_all_hours_destination%22%3Anull%2C%22static_in_hours_destination%22%3Anull%2C%22target%22%3Anull%2C%22type%22%3Anull%7D&client_messages=%7B%7D&client_info=%7B%22url%22%3A%22https%3A%2F%2Fwww.amplifonusa.com%2Four-program%2Fclinic-locator%2Fsearch-results-page%3Faddr%3D%26lat%3D{lat}%26long%3D{lng}%22%2C%22referrer%22%3A%22%22%2C%22cores%22%3A4%2C%22platform%22%3A%22Linux%20x86_64%22%2C%22screenWidth%22%3A1366%2C%22screenHeight%22%3A768%2C%22language%22%3A%22en-US%22%7D&request_data=%5B%7B%22request_id%22%3A%22%2B18778467074%22%2C%22advertiser_campaign_id_from_network%22%3A%22AMPLUNIV01%22%2C%22params%22%3A%7B%22static_all_hours_destination%22%3A%22%2B18778467074%22%2C%22invoca_detected_destination%22%3A%22%2B18778467074%22%7D%7D%2C%7B%22request_id%22%3A%22%2B18883090026%22%2C%22advertiser_campaign_id_from_network%22%3A%22AMPLUNIV01%22%2C%22params%22%3A%7B%22static_all_hours_destination%22%3A%22%2B18883090026%22%2C%22invoca_detected_destination%22%3A%22%2B18883090026%22%7D%7D%5D&destination_settings=%7B%22paramName%22%3A%22static_all_hours_destination%22%7D&jsoncallback=json_rr11&"
                try:
                    phone = json.loads(
                        http.get(url, headers=header1(lat, lng))
                        .text.replace("json_rr11(", "")
                        .replace(");", "")
                    )[1]["formattedNumber"]
                except:
                    pass

                street_address = _["address2"]
                if _["address3"]:
                    street_address += " " + _["address3"]
                yield SgRecord(
                    page_url="https://www.amplifonusa.com/our-program/clinic-locator",
                    store_number=_["id"],
                    location_name=_["shopname"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["postalcode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], granularity=Grain_4()
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
