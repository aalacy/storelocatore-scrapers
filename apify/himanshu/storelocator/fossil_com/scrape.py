import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fossil_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    return_main_object = []
    countries = ["US", "CA", "UK"]
    for country_code in countries:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        }
        base_url = "https://www.fossil.com"

        r = session.get(
            'https://hosted.where2getit.com/fossil/local/ajax?&xml_request=xml_request: <request><appkey>269B11D6-E81F-11E3-A0C3-A70A0D516365</appkey><formdata id="getlist"><objectname>Locator::Store</objectname><order>CITY</order><limit>10000</limit><where><country><eq>{}</eq></country><state><eq></eq></state><or><fossil_store><eq>1</eq></fossil_store><fossil_outlet><eq>1</eq></fossil_outlet></or></where></formdata></request>'.format(
                country_code
            ),
            headers=headers,
        )
        soup = BeautifulSoup(r.text, "lxml")

        # it will used in store data.
        locator_domain = base_url
        location_name = ""
        page_url = "<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        for script in soup.find_all("poi"):

            location_name = script.find("name").text
            location_type = script.find("icon").text
            store_number = script.find("clientkey").text
            street_address = (
                script.find("address1").text + " " + script.find("address2").text
            )
            city = script.find("city").text
            state = script.find("state").text
            if len(state) <= 0:
                state = script.find("province").text

            if len(state) > 0:
                page_url = "https://stores.fossil.com/{}/{}/{}/".format(
                    state, city, store_number
                )

            zipp = script.find("postalcode").text
            country_code = script.find("country").text
            latitude = script.find("latitude").text
            longitude = script.find("longitude").text
            phone = script.find("phone").text.replace("&#xa0;", "")

            if len(location_name) == 0:
                location_name = "<MISSING>"

            if len(street_address) == 0:
                street_address = "<MISSING>"

            if len(city) == 0:
                city = "<MISSING>"

            if len(state) == 0:
                state = "<MISSING>"

            if len(zipp) == 0:
                zipp = "<MISSING>"

            if len(country_code) == 0:
                country_code = "US"

            if len(latitude) == 0:
                latitude = "<MISSING>"

            if len(longitude) == 0:
                longitude = "<MISSING>"

            if len(phone) == 0:
                phone = "<MISSING>"

            if (
                len(script.find("sundayopen").text) > 0
                or len(script.find("mondayopen").text) > 0
                or len(script.find("tuesdayopen").text) > 0
                or len(script.find("wednesdayopen").text) > 0
                or len(script.find("thursdayopen").text) > 0
                or len(script.find("fridayopen").text) > 0
                or len(script.find("saturdayopen").text) > 0
            ):
                hours_of_operation = (
                    "Sunday:"
                    + script.find("sundayopen").text
                    + " - "
                    + script.find("sundayclose").text
                    + ", "
                    + "Monday:"
                    + script.find("mondayopen").text
                    + " - "
                    + script.find("mondayclose").text
                    + ", "
                    + "Tuesday:"
                    + script.find("tuesdayopen").text
                    + " - "
                    + script.find("tuesdayclose").text
                    + ", "
                    + "Wednesday:"
                    + script.find("wednesdayopen").text
                    + " - "
                    + script.find("wednesdayclose").text
                    + ", "
                    + "Thursday:"
                    + script.find("thursdayopen").text
                    + " - "
                    + script.find("thursdayclose").text
                    + ", "
                    + "Friday:"
                    + script.find("fridayopen").text
                    + " - "
                    + script.find("fridayclose").text
                    + ", "
                    + "Saturday:"
                    + script.find("saturdayopen").text
                    + " - "
                    + script.find("saturdayclose").text
                )
            else:
                hours_of_operation = "<MISSING>"

            store = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
