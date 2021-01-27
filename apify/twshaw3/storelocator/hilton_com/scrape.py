import csv
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
from sglogging import SgLogSetup

headers = {
    "Content-Type": "application/json",
    "cache-control": "no-cache",
}

logger = SgLogSetup().get_logger("hilton_com")


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def filter_zones(zones):
    for zone in zones:
        countries = {x["countryCode"] for x in zone["countries"]}
        if {"US", "CA"}.intersection(countries) and "HI" in zone["brandCodes"]:
            yield zone


@retry(stop=stop_after_attempt(3))
def get_locations(zone):
    logger.info(zone["countries"])
    session = SgRequests()
    url = "https://www.hilton.com/graphql/customer"
    querystring = {
        "appName": "dx-shop-dream-ui",
        "operationName": "hotelSummaryOptions",
        "queryType": "zone",
    }
    payload = (
        '{"operationName":"hotelSummaryOptions","variables":{"brandCodes":[],"currencyCode":"usd","language":"en","zone":{"x":'
        + str(zone["id"]["x"])
        + ',"y":'
        + str(zone["id"]["y"])
        + '}},"query":"query hotelSummaryOptions($brandCodes: [String!]!, $currencyCode: String!, $language: String!, $zone: HotelZoneInput) {\\n  hotelSummaryOptions(brandCodes: $brandCodes, language: $language, input: {zone: $zone}) {\\n    hotels {\\n      _id: ctyhocn\\n      amenityIds\\n      brandCode\\n      ctyhocn\\n      currencyCode\\n      distance\\n      distanceFmt\\n      homeUrl\\n      homepageUrl\\n      name\\n      phoneNumber\\n      address {\\n        addressFmt\\n        addressLine1\\n        addressLine2\\n        city\\n        country\\n        countryName\\n        postalCode\\n        state\\n        stateName\\n        __typename\\n      }\\n      coordinate {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      thumbImage {\\n        hiResSrc(height: 430, width: 612)\\n        __typename\\n      }\\n      thumbnail: masterImage(variant: searchPropertyImageThumbnail) {\\n        altText\\n        variants {\\n          size\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      leadRate {\\n        lowest {\\n          rateAmount(currencyCode: $currencyCode, decimal: 0, strategy: trunc)\\n          rateAmountFmt(decimal: 0, strategy: trunc)\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
    )
    response = session.post(url, data=payload, headers=headers, params=querystring)
    json_data = response.json()
    k = json_data["data"]["hotelSummaryOptions"]["hotels"]
    for j in k:
        if j["address"]["country"] not in ("US", "CA"):
            continue
        if j["brandCode"] not in ("HI"):
            continue
        store = []
        store.append("hilton.com")
        store.append(j["name"])
        store.append(j["address"]["addressLine1"])
        store.append(j["address"]["city"])
        store.append(j["address"]["stateName"])
        store.append(j["address"]["postalCode"])
        store.append(j["address"]["country"])
        store.append("<MISSING>")
        store.append(j["phoneNumber"] if j["phoneNumber"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(j["coordinate"]["latitude"])
        store.append(j["coordinate"]["longitude"])
        store.append("<MISSING>")
        store.append(j["homepageUrl"])
        yield store


def fetch_data():
    keys = set()
    url = "https://www.hilton.com/graphql/customer?appName=dx-shop-dream-ui&operationName=hotelMapZones"
    payload = '{"operationName":"hotelMapZones","variables":{"brandCode":""},"query":"query hotelMapZones($brandCode: String) {\\n  hotelMapZones(brandCode: $brandCode) {\\n    id {\\n      x\\n      y\\n      __typename\\n    }\\n    bounds {\\n      southwest {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      northeast {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      __typename\\n    }\\n    countries {\\n      countryCode\\n      stateCodes\\n      __typename\\n    }\\n    brandCodes\\n    __typename\\n  }\\n}\\n"}'
    session = SgRequests()
    data = session.post(url, data=payload, headers=headers).json()
    zones = list(filter_zones(data["data"]["hotelMapZones"]))
    logger.info(f"scraping {len(zones)} zones")
    for zone in zones:
        for loc in get_locations(zone):
            if loc is not None:
                key = "|".join(loc[1:7])
                if key not in keys:
                    keys.add(key)
                    yield loc


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
