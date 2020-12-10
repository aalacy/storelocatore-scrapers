import csv
from sgrequests import SgRequests
import phonenumbers
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("woodspring_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=100,
    )
    logger.info(coords.items_remaining())
    main_url = "https://www.woodspring.com"
    addresses = []
    for cord in coords:
        logger.info("")
        result_coords = []
        x = cord[0]
        y = cord[1]
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        }
        r = session.get(
            "https://www-api.woodspring.com/v2/hotel/hotels?lat="
            + str(x)
            + "&lng="
            + str(y)
            + "&max=200&offset=0&radius=200"
        )
        if "searchResults" not in r.json():
            continue
        data = r.json()["searchResults"]
        for store_data in data:
            result_coords.append(
                (
                    store_data["geographicLocation"]["latitude"],
                    store_data["geographicLocation"]["longitude"],
                )
            )
            if (
                store_data["address"]["countryCode"] != "US"
                and store_data["address"]["countryCode"] != "CA"
            ):
                continue
            store = []
            store.append(main_url)
            store.append(store_data["hotelName"])
            location_request = session.get(
                "https://www-api.woodspring.com/v2/hotel/hotels/"
                + str(store_data["hotelId"])
                + "?include=location,phones,amenities",
                headers=headers,
            )
            location_data = location_request.json()
            if "hotelStatus" in location_data["hotelInfo"]["hotelSummary"]:
                if (
                    location_data["hotelInfo"]["hotelSummary"]["hotelStatus"]
                    == "Closed"
                ):
                    continue
            add = location_data["hotelInfo"]["hotelSummary"]["addresses"][0]
            try:
                phone = phonenumbers.format_number(
                    phonenumbers.parse(
                        str(
                            location_data["hotelInfo"]["hotelSummary"]["phones"][1][
                                "countryAccessCode"
                            ]
                            + location_data["hotelInfo"]["hotelSummary"]["phones"][1][
                                "areaCode"
                            ]
                            + location_data["hotelInfo"]["hotelSummary"]["phones"][1][
                                "number"
                            ]
                        ),
                        "US",
                    ),
                    phonenumbers.PhoneNumberFormat.NATIONAL,
                )
            except:
                phone = phonenumbers.format_number(
                    phonenumbers.parse(
                        str(
                            location_data["hotelInfo"]["hotelSummary"]["phones"][-1][
                                "number"
                            ]
                        ),
                        "US",
                    ),
                    phonenumbers.PhoneNumberFormat.NATIONAL,
                )
            store.append(",".join(add["street"]))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(add["cityName"] if add["cityName"] else "<MISSING>")
            if "," + store[-1] + "," in store[2]:
                store[2] = store[2].split("," + store[-1])[0]
            store.append(
                add["subdivisionCode"] if add["subdivisionCode"] else "<MISSING>"
            )
            store.append(add["postalCode"] if add["postalCode"] else "<MISSING>")
            store.append(add["countryCode"])
            store.append("<MISSING>")
            store.append(
                phone.replace("111111111", "(863) 578-3658").replace(
                    "13213681", "<MISSING>"
                )
            )
            store.append("<MISSING>")
            store.append(store_data["geographicLocation"]["latitude"])
            store.append(store_data["geographicLocation"]["longitude"])
            try:
                mon = (
                    location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["mon"][0]["startTime"]
                    + "-"
                    + location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["mon"][0]["endTime"]
                )
                tue = (
                    location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["tue"][0]["startTime"]
                    + "-"
                    + location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["tue"][0]["endTime"]
                )
                wed = (
                    location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["wed"][0]["startTime"]
                    + "-"
                    + location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["wed"][0]["endTime"]
                )
                thu = (
                    location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["thu"][0]["startTime"]
                    + "-"
                    + location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["thu"][0]["endTime"]
                )
                fri = (
                    location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["fri"][0]["startTime"]
                    + "-"
                    + location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["fri"][0]["endTime"]
                )
                sat = (
                    location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["sat"][0]["startTime"]
                    + "-"
                    + location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["sat"][0]["endTime"]
                )
                sun = (
                    location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["sun"][0]["startTime"]
                    + "-"
                    + location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1][
                        "hoursOfOperation"
                    ]["sun"][0]["endTime"]
                )
                hoo = (
                    "mon "
                    + mon
                    + ", tue "
                    + tue
                    + ", wed "
                    + wed
                    + ", thu "
                    + thu
                    + ", fri "
                    + fri
                    + ", sat "
                    + sat
                    + ", sun "
                    + sun
                )
            except KeyError:
                hoo = "<MISSING>"
            store.append(hoo)
            store.append(main_url + str(store_data["hotelUri"]))
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
