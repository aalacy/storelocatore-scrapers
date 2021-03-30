import csv

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def fetch_data():
    base_url = "https://familyexpress.com/api/locations/place"
    r = session.get(base_url).json()["places"]
    return_main_object = []
    for location in r:
        if location["yextData"]:
            store = []
            try:
                if "isClosed" not in location["yextData"]["hours"]["sunday"]:
                    hours = (
                        " sunday : "
                        + location["yextData"]["hours"]["sunday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["sunday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours = " sunday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["monday"]:
                    hours += (
                        " monday : "
                        + location["yextData"]["hours"]["monday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["monday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " monday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["monday"]:
                    hours += (
                        " monday : "
                        + location["yextData"]["hours"]["monday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["monday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " tuesday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["tuesday"]:
                    hours += (
                        " tuesday : "
                        + location["yextData"]["hours"]["tuesday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["tuesday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " wednesday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["wednesday"]:
                    hours += (
                        " wednesday : "
                        + location["yextData"]["hours"]["wednesday"]["openIntervals"][
                            0
                        ]["start"]
                        + "-"
                        + location["yextData"]["hours"]["wednesday"]["openIntervals"][
                            0
                        ]["end"]
                    )
                else:
                    hours += " wednesday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["thursday"]:
                    hours += (
                        " thursday : "
                        + location["yextData"]["hours"]["thursday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["thursday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " thursday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["friday"]:
                    hours += (
                        " friday : "
                        + location["yextData"]["hours"]["friday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["friday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " friday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["saturday"]:
                    hours += (
                        " saturday : "
                        + location["yextData"]["hours"]["saturday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["saturday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " saturday : Closed"
            except:
                hours = "<MISSING>"
            store.append("https://familyexpress.com")
            store.append(location["yextData"]["c_subName"])
            store.append(location["yextData"]["address"]["line1"])
            store.append(location["yextData"]["address"]["city"])
            store.append(location["yextData"]["address"]["region"])
            store.append(location["yextData"]["address"]["postalCode"])
            store.append(location["yextData"]["address"]["countryCode"])
            store.append(location["storeId"])
            store.append(location["yextData"]["mainPhone"])
            store.append("<MISSING>")
            store.append(location["yextData"]["yextDisplayCoordinate"]["latitude"])
            store.append(location["yextData"]["yextDisplayCoordinate"]["longitude"])
            store.append(hours.strip())
            store.append("https://familyexpress.com/locations")
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
