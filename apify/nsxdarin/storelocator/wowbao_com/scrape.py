from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("wowbao_com")

url_ql = "https://wowbao.order.online/graphql"


def fetch_data():
    url = "https://api.storepoint.co/v1/15fe0bd667ae7b/locations?lat=41.8756&long=-87.6244&radius=500000"
    r = session.get(url, headers=headers)
    website = "wowbao.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    hours_of_operation = "<MISSING>"
    for item in json.loads(r.content)["results"]["locations"]:
        store = item["id"]
        lat = item["loc_lat"]
        lng = item["loc_long"]
        name = item["name"]
        addinfo = item["streetaddress"]
        add = "<MISSING>"
        if addinfo.count(",") == 1:
            city = addinfo.split(",")[0]
            state = addinfo.split(",")[1].strip()
        else:
            add = addinfo.split(",")[0]
            city = addinfo.split(",")[1].strip()
            state = addinfo.split(",")[2].strip()
        zc = "<MISSING>"
        phone = "<MISSING>"
        loc = item["website"]
        if "order.online" in loc:
            try:
                """
                CHECKS PRESENCE OF GRAPHQL ENDPOINT TO UPDATE CITY, STREET, ZIP and HOO etc
                """
                graphql_id = re.findall(r"(\d+)/", item["website"])[0]
                payload_ql = {
                    "operationName": "storepageFeed",
                    "variables": {
                        "fulfillmentType": "Delivery",
                        "storeId": f"{graphql_id}",
                        "isMerchantPreview": False,
                        "includeNestedOptions": False,
                        "includeQuickAddContext": False,
                    },
                    "query": "query storepageFeed($storeId: ID!, $menuId: ID, $isMerchantPreview: Boolean, $fulfillmentType: FulfillmentType, $cursor: String){storepageFeed(storeId: $storeId, menuId: $menuId, isMerchantPreview: $isMerchantPreview, fulfillmentType: $fulfillmentType, cursor: $cursor){storeHeader { id address { lat lng city street state displayAddress cityLink __typename} __typename} menuBook{id name displayOpenHours __typename } __typename}}",
                }
                response_ql = session.post(
                    url_ql, json=payload_ql, headers=headers
                ).json()
                add = response_ql["data"]["storepageFeed"]["storeHeader"]["address"][
                    "street"
                ]
                zc = re.findall(
                    r"[A-Z]{2} ([A-Z0-9 ]*)",
                    response_ql["data"]["storepageFeed"]["storeHeader"]["address"][
                        "displayAddress"
                    ],
                )[0]
                state = re.findall(
                    r"[A-Z]{2}",
                    response_ql["data"]["storepageFeed"]["storeHeader"]["address"][
                        "displayAddress"
                    ],
                )[0]
                city = response_ql["data"]["storepageFeed"]["storeHeader"]["address"][
                    "city"
                ]
                hours = response_ql["data"]["storepageFeed"]["menuBook"][
                    "displayOpenHours"
                ]
                ooh = [
                    day.title() + f": {hours}"
                    for day in [
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                        "sunday",
                    ]
                ]
                hours_of_operation = ", ".join(ooh)
                raw_address = response_ql["data"]["storepageFeed"]["storeHeader"][
                    "address"
                ]["displayAddress"]

            except:
                pass

            yield SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
