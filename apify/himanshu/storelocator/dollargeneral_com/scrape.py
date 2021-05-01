import csv
from datetime import datetime

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


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


def fetch_data():
    addresses = []
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }
    locator_domain = "medicineshoppe.com"

    max_results = 250
    max_distance = 50

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    location_url = "http://hosted.where2getit.com/dollargeneral/rest/locatorsearch?like=0.9394142712975708"

    for zip_code in search:
        data = (
            '{"request":{"appkey":"9E9DE426-8151-11E4-AEAC-765055A65BB0","formdata":{"geoip":false,"dataview":"store_default","geolocs":{"geoloc":[{"addressline":"'
            + str(zip_code)
            + '","country":"US","latitude":"","longitude":""}]},"searchradius":"10|20|50|100","where":{"nci":{"eq":""},"and":{"PROPANE":{"eq":""},"REDBOX":{"eq":""},"RUGDR":{"eq":""},"MULTICULTURAL_HAIR":{"eq":""},"TYPE_ID":{"eq":""},"DGGOCHECKOUT":{"eq":""},"FEDEX":{"eq":""},"DGGOCART":{"eq":""}}},"false":"0"}}}'
        )
        try:
            loc = session.post(location_url, headers=headers, data=data).json()
        except:
            pass

        locator_domain = "https://www.dollargeneral.com/"
        country_code = "US"
        store_number = ""
        location_type = ""
        hours_of_operation = ""

        if "collection" in loc["response"]:
            for data in loc["response"]["collection"]:
                store_number = data["name"].split("#")[-1]
                try:
                    hours_of_operation = (
                        " Monday "
                        + str(
                            datetime.strptime(
                                data["opening_time_mon"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + " - "
                        + str(
                            datetime.strptime(
                                data["closing_time_mon"]
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + ","
                        + " Tuesday "
                        + str(
                            datetime.strptime(
                                data["opening_time_tue"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + " - "
                        + str(
                            datetime.strptime(
                                data["closing_time_tue"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + ","
                        + " Wednesday "
                        + str(
                            datetime.strptime(
                                data["opening_time_wed"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + " - "
                        + str(
                            datetime.strptime(
                                data["closing_time_wed"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + ","
                        + " Thursday "
                        + str(
                            datetime.strptime(
                                data["opening_time_thu"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + " - "
                        + str(
                            datetime.strptime(
                                data["closing_time_thu"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + ","
                        + " Friday "
                        + str(
                            datetime.strptime(
                                data["opening_time_fri"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + " - "
                        + str(
                            datetime.strptime(
                                data["closing_time_fri"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + ","
                        + " Saturday "
                        + str(
                            datetime.strptime(
                                data["opening_time_sat"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + " - "
                        + str(
                            datetime.strptime(
                                data["closing_time_sat"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + ","
                        + " Sunday "
                        + str(
                            datetime.strptime(
                                data["opening_time_sun"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                        + " - "
                        + str(
                            datetime.strptime(
                                data["closing_time_sun"]
                                .replace("7.:00", "07:00")
                                .replace("8.:00", "08:00")
                                .replace("24:00", "00:00"),
                                "%H:%M",
                            ).strftime("%I:%M %p")
                        )
                    )
                except:
                    hours_of_operation = "<MISSING>"

                p = store_number.strip()
                page_url = (
                    "http://www2.dollargeneral.com/Savings/Circulars/Pages/index.aspx?store_code="
                    + str(p)
                )
                store = [
                    locator_domain,
                    data["name"],
                    data["address1"],
                    data["city"],
                    data["state"],
                    data["postalcode"],
                    country_code,
                    store_number,
                    data["phone"],
                    location_type,
                    data["latitude"],
                    data["longitude"],
                    hours_of_operation,
                    page_url,
                ]
                search.found_location_at(data["latitude"], data["longitude"])
                if store[2] + store[-3] in addresses:
                    continue
                addresses.append(store[2] + store[-3])
                store = [x.strip() if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
