from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = 'https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=7d3f010c5d39e1427b1ef79803fb493e&jsLibVersion=v1.7.5&sessionTrackingEnabled=true&input=bbva near me&experienceKey=bbvaconfig&version=PRODUCTION&filters={"$or":[{"c_bBVAType":{"$eq":"BBVA Branch"}},{"c_bBVAType":{"$eq":"BBVA ATM"}}]}&facetFilters={}&verticalKey=locations&limit=20&offset=0&queryId=6b412096-ed5d-4cd5-9f11-e040fc766f8c&locale=en&referrerPageUrl=https://www.bbvausa.com/&source=STANDARD'
    domain = "bbvausa.com"

    data = session.get(start_url).json()
    for offset in range(0, data["response"]["resultsCount"] + 20, 20):
        data = session.get(
            add_or_replace_parameter(start_url, "offset", str(offset))
        ).json()
        all_locations = data["response"]["results"]

        for poi in all_locations:
            location_name = poi["data"].get("c_bBVAName")
            if not location_name:
                location_name = poi["data"]["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["data"]["address"]["line1"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["data"]["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["data"]["address"]["region"]
            state = state if state else "<MISSING>"
            zip_code = poi["data"]["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["data"]["address"]["countryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["data"]["id"]
            phone = poi["data"]["mainPhone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["data"]["c_bBVAType"][0]
            location_type = location_type if location_type else "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if poi["data"].get("cityCoordinate"):
                latitude = poi["data"]["cityCoordinate"]["latitude"]
                longitude = poi["data"]["cityCoordinate"]["longitude"]
            elif poi["data"].get("displayCoordinate"):
                latitude = poi["data"]["displayCoordinate"]["latitude"]
                longitude = poi["data"]["displayCoordinate"]["longitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            if poi["data"].get("hours"):
                for day, hours in poi["data"]["hours"].items():
                    if type(hours) == str:
                        continue
                    if day == "holidayHours":
                        continue
                    if hours.get("openIntervals"):
                        hours_of_operation.append(
                            "{} {} - {}".format(
                                day,
                                hours["openIntervals"][0]["start"],
                                hours["openIntervals"][0]["end"],
                            )
                        )
                    if hours.get("isClosed"):
                        hours_of_operation.append("{} - closed".format(day))
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            store_url = poi["data"].get("website")
            if not store_url:
                store_url = "https://www.bbvausa.com/bank-atm/{}/{}/{}/{}/".format(
                    state,
                    city,
                    street_address.replace(" ", "-"),
                    location_name.replace(" ", "-"),
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
