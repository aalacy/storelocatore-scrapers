# -*- coding: utf-8 -*-
import json
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "underarmour.com"
    start_url = (
        "https://hosted.where2getit.com/underarmour/2015/rest/locatorsearch?lang=en_US"
    )

    body = '{"request":{"appkey":"24358678-428E-11E4-8BC2-2736C403F339","formdata":{"geoip":false,"dataview":"store_default","order":"UASPECIALITY, UAOUTLET, AUTHORIZEDDEALER, rank,_distance","limit":200,"geolocs":{"geoloc":[{"addressline":"","country":"","latitude":%s,"longitude":%s,"state":"","province":"","city":"","address1":"","postalcode":""}]},"searchradius":"200|210|220|230|240|250","where":{"or":{"UASPECIALITY":{"eq":"1"},"UAOUTLET":{"eq":"1"},"AUTHORIZEDDEALER":{"eq":""}}},"false":"0"}}}'
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    all_coords = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL, expected_search_radius_miles=200
    )
    for lat, lng in all_coords:
        response = session.post(start_url, data=body % (lat, lng), headers=headers)
        data = json.loads(response.text)
        if not data["response"].get("collection"):
            continue

        for poi in data["response"]["collection"]:
            location_name = poi["name"]
            street_address = (
                poi["address1"].replace("&#xe9;", "é").replace("&#xe8;", "è")
            )
            city = poi["city"]
            state = poi["state"]
            if not state:
                state = poi["province"]
            zip_code = poi["postalcode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country"]
            store_number = poi["clientkey"]
            phone = poi["phone"]
            if phone:
                phone = phone.replace("...", "").strip()
                if country_code == "TH":
                    phone = phone.split("/")[0]
            location_type = poi["icon"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hours_of_operation = []
            hours_dict = {}
            for key, value in poi.items():
                if "date" in key:
                    continue
                if "temp" in key:
                    continue
                if "close" in key:
                    day = key.replace("close", "")
                    if hours_dict.get(day):
                        hours_dict[day]["closes"] = value
                    else:
                        hours_dict[day] = {}
                        hours_dict[day]["closes"] = value
                if "open" in key:
                    day = key.replace("open", "")
                    if hours_dict.get(day):
                        hours_dict[day]["opens"] = value
                    else:
                        hours_dict[day] = {}
                        hours_dict[day]["closes"] = value
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            store_url = "https://www.underarmour.com/en-us/store-locator"
            if country_code.lower() == "us":
                store_url = "http://store-locations.underarmour.com/{}/{}/{}/".format(
                    state, city.replace(" ", "-"), store_number
                )

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
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
