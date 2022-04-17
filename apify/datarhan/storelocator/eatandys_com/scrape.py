import json
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameters

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "eatandys.com"
    base_url = "https://locations.eatandys.com/"
    start_url = "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token=WYEMXMEMZMFGMIDG&country=US&multi_account=false"

    response = session.get(start_url)
    data = json.loads(response.text)
    for poi in data["locations"]:
        store_url = urljoin(base_url, poi["llp_url"])
        street_address = poi["store_info"]["address"]
        city = poi["store_info"]["locality"]
        state = poi["store_info"]["region"]
        zip_code = poi["store_info"]["postcode"]
        country_code = poi["store_info"]["country"]

        loc_url = "https://api.momentfeed.com/v1/analytics/api/llp.json"
        params = {
            "address": street_address,
            "locality": city,
            "multi_account": "false",
            "pageSize": "30",
            "region": state,
        }
        loc_url = add_or_replace_parameters(loc_url, params)
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
            "authorization": "WYEMXMEMZMFGMIDG",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        }
        loc_response = session.get(loc_url, headers=headers)
        data = json.loads(loc_response.text)
        if type(data) == dict and data['message'] == 'No matching locations found':
            continue
        location_name = data[0]["store_info"]["name"]
        phone = data[0]["store_info"]["phone"]
        latitude = data[0]["store_info"]["latitude"]
        longitude = data[0]["store_info"]["longitude"]
        hours = data[0]["store_info"]["hours"].split(";")[:-1]
        hours = [elem[2:].replace(",", " - ").replace("00", ":00") for elem in hours]
        days = [
            "Monday",
            "Tuesday",
            "Wednsday",
            "Thursday",
            "Friday",
            "Satarday",
            "Sunday",
        ]
        hours_of_operation = list(map(lambda day, hour: day + " " + hour, days, hours))
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
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
            hours_of_operation=hours_of_operation,
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
