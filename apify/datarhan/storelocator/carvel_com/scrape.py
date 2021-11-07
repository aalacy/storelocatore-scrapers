from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "carvel.com"
    user_agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }

    all_locations = []
    start_url = 'https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=carvel-answers&api_key=7425eae4ff5d283ef2a3542425aade29&v=20190101&version=PRODUCTION&locale=en&input=Restaurants near me&verticalKey=restaurants&limit=20&offset=0&retrieveFacets=true&facetFilters={"c_carvelServices":[]}&sessionTrackingEnabled=true&sortBys=[]&referrerPageUrl=&source=STANDARD&queryId=8392232e-0128-4105-870a-d373c33361bd&jsLibVersion=v1.9.2'
    data = session.get(start_url, headers=user_agent).json()
    total = data["response"]["resultsCount"]
    all_locations = data["response"]["results"]
    for offset in range(20, total + 20, 20):
        data = session.get(
            add_or_replace_parameter(start_url, "offset", str(offset))
        ).json()
        all_locations += data["response"]["results"]

    for poi in all_locations:
        page_url = poi["data"]["websiteUrl"]["displayUrl"]
        if "https://www" in page_url:
            continue
        hoo = []
        if poi["data"].get("hours"):
            for day, hours in poi["data"]["hours"].items():
                if type(hours) == list:
                    continue
                if day == "reopenDate":
                    continue
                if hours.get("openIntervals"):
                    hoo.append(
                        f'{day} {hours["openIntervals"][0]["start"]} - {hours["openIntervals"][0]["end"]}'
                    )
                else:
                    hoo.append(f"{day} closed")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["data"]["c_nAPDescription"]["title"].replace(
                "Welcome to Carvel ", ""
            ),
            street_address=poi["data"]["address"]["line1"],
            city=poi["data"]["address"]["city"],
            state=poi["data"]["address"]["region"],
            zip_postal=poi["data"]["address"]["postalCode"],
            country_code=poi["data"]["address"]["countryCode"],
            store_number=poi["data"]["id"],
            phone=poi["data"].get("mainPhone"),
            location_type=poi["data"]["name"],
            latitude=poi["data"]["yextDisplayCoordinate"]["latitude"],
            longitude=poi["data"]["yextDisplayCoordinate"]["longitude"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
