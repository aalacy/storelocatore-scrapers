# -*- coding: utf-8 -*-
import json

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bmo.com"
    start_url = "https://branchlocator.bmo.com/rest/locatorsearch?lang=en_US"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
    }
    all_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        expected_search_radius_miles=20,
    )
    for lat, lng in all_codes:
        body = '{"request":{"appkey":"343095D0-C235-11E6-93AB-1BF70C70A832","formdata":{"geoip":false,"dataview":"store_default","limit":50,"google_autocomplete":"true","geolocs":{"geoloc":[{"addressline":"","country":"","latitude":%s,"longitude":%s}]},"searchradius":"250","softmatch":"1","where":{"and":{"wheelchair":{"eq":""},"safedepositsmall":{"eq":""},"transit":{"eq":""},"languages":{"ilike":""},"saturdayopen":{"ne":""},"sundayopen":{"ne":""},"abmsaturdayopen":{"ne":""},"abmsundayopen":{"ne":""},"grouptype":{"eq":"BMOBranches"}}},"false":"0"}}}'
        response = session.post(start_url, data=body % (lat, lng), headers=headers)
        data = json.loads(response.text)

        if not data["response"].get("collection"):
            continue

        for poi in data["response"]["collection"]:
            location_name = poi["name"]
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            city = poi["city"]
            state = poi["state"]
            if not state:
                state = poi["province"]
            zip_code = poi["postalcode"]
            country_code = poi["country"]
            store_number = poi["uid"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["grouptype"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            store_url = f"https://branches.bmo.com/{state}/{city.lower().replace(' ', '-')}/{poi['clientkey']}/"
            hours_of_operation = []
            hours = {}
            for key, value in poi.items():
                if key in ["grandopendate", "nowopen"]:
                    continue
                if not value:
                    continue
                if "abm" in key:
                    continue
                if "open" in key:
                    day = key.replace("open", "")
                    if "closed" in value:
                        hours[day] = "closed"
                    else:
                        closes = value[:-2] + ":" + value[-2:]
                        if hours.get(day):
                            hours[day]["open"] = closes
                        else:
                            hours[day] = {}
                            hours[day]["open"] = closes
                if "close" in key:
                    day = key.replace("close", "")
                    if "closed" in value:
                        hours[day] = "closed"
                    else:
                        closes = value[:-2] + ":" + value[-2:]
                        if hours.get(day):
                            hours[day]["close"] = closes
                        else:
                            hours[day] = {}
                            hours[day]["close"] = closes

            for day, time in hours.items():
                if time == "closed":
                    hours_of_operation.append("{} closed".format(day))
                else:
                    hours_of_operation.append(
                        "{} {} - {}".format(day, time["open"], time["close"])
                    )
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
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
