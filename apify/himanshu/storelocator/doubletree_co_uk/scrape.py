from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("hilton.com")

session = SgRequests()


def fetch_data(sgw: SgWriter):
    address = []
    headers = {
        "Content-Type": "application/json",
        "cache-control": "no-cache",
    }
    url = "https://www.hilton.com/graphql/customer?appName=dx-shop-search-ui&operationName=hotelMapZones"
    payload = '{"operationName":"hotelMapZones","variables":{"brandCode":"DT"},"query":"query hotelMapZones($brandCode: String) {\\n  hotelMapZones(brandCode: $brandCode) {\\n    id {\\n      x\\n      y\\n      __typename\\n    }\\n    bounds {\\n      southwest {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      northeast {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      __typename\\n    }\\n    countries {\\n      countryCode\\n      stateCodes\\n      __typename\\n    }\\n    brandCodes\\n    __typename\\n  }\\n}\\n"}'
    data = session.post(url, data=payload, headers=headers).json()

    for zone in data["data"]["hotelMapZones"]:
        url = "https://www.hilton.com/graphql/customer"
        querystring = {
            "appName": "dx-shop-dream-ui",
            "operationName": "hotelSummaryOptions",
            "queryType": "zone",
        }
        payload = (
            '{"operationName":"hotelSummaryOptions","variables":{"brandCodes":["DT"],"currencyCode":"usd","language":"en","zone":{"x":'
            + str(zone["id"]["x"])
            + ',"y":'
            + str(zone["id"]["y"])
            + '}},"query":"query hotelSummaryOptions($brandCodes: [String!]!, $currencyCode: String!, $language: String!, $zone: HotelZoneInput) {\\n  hotelSummaryOptions(brandCodes: $brandCodes, language: $language, input: {zone: $zone}) {\\n    hotels {\\n      _id: ctyhocn\\n      amenityIds\\n      brandCode\\n      ctyhocn\\n      currencyCode\\n      distance\\n      distanceFmt\\n      homeUrl\\n      homepageUrl\\n      name\\n      phoneNumber\\n      address {\\n        addressFmt\\n        addressLine1\\n        addressLine2\\n        city\\n        country\\n        countryName\\n        postalCode\\n        state\\n        stateName\\n        __typename\\n      }\\n      coordinate {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      thumbImage {\\n        hiResSrc(height: 430, width: 612)\\n        __typename\\n      }\\n      thumbnail: masterImage(variant: searchPropertyImageThumbnail) {\\n        altText\\n        variants {\\n          size\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      leadRate {\\n        lowest {\\n          rateAmount(currencyCode: $currencyCode, decimal: 0, strategy: trunc)\\n          rateAmountFmt(decimal: 0, strategy: trunc)\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
        )
        json_data = session.post(
            url, data=payload, headers=headers, params=querystring
        ).json()
        k = json_data["data"]["hotelSummaryOptions"]["hotels"]
        for j in k:
            if j["address"]["country"] != "GB":
                continue
            if j["brandCode"] not in ("DT"):
                continue
            store = []
            store.append("https://www.hilton.com")
            store.append(j["name"])
            store.append(j["address"]["addressLine1"])
            store.append(j["address"]["city"])
            store.append(j["address"]["stateName"])
            store.append(j["address"]["postalCode"])
            store.append(j["address"]["country"])
            store.append("<MISSING>")
            store.append(j["phoneNumber"] if j["phoneNumber"] else "<MISSING>")
            store.append(j["brandCode"].replace("DT", "DoubleTree by Hilton"))
            store.append(j["coordinate"]["latitude"])
            store.append(j["coordinate"]["longitude"])
            store.append("<MISSING>")
            store.append(j["homepageUrl"])
            if store[2] in address:
                continue
            address.append(store[2])
            logger.info(j["address"]["addressLine1"])

            sgw.write_row(
                SgRecord(
                    locator_domain=store[0],
                    location_name=store[1],
                    street_address=store[2],
                    city=store[3],
                    state=store[4],
                    zip_postal=store[5],
                    country_code=store[6],
                    store_number=store[7],
                    phone=store[8],
                    location_type=store[9],
                    latitude=store[10],
                    longitude=store[11],
                    hours_of_operation=store[12],
                    page_url=store[13],
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
