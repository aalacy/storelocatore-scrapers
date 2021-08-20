import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://czqk28jt.apicdn.sanity.io/v1/data/query/prod_plk_us?query=*%5B%20_type%20%3D%3D%20%27restaurant%27%26%26%20environment%20%3D%3D%20%24environment%26%26%20latitude%20%3E%20%24minLat%26%26%20latitude%20%3C%20%24maxLat%26%26%20longitude%20%3E%20%24minLng%26%26%20longitude%20%3C%20%24maxLng%26%26%20status%20%3D%3D%20%24status%20%5D%20%7Corder((%24userLat%20-%20latitude)%20**%202%20%2B%20(%24userLng%20-%20longitude)%20**%202)%5B%24offset...(%24offset%20%2B%20%24limit)%5D%20%7B_id%2CdeliveryHours%2CdiningRoomHours%2CdrinkStationType%2CdriveThruHours%2CdriveThruLaneType%2Cemail%2CfranchiseGroupId%2CfranchiseGroupName%2ChasBreakfast%2ChasBurgersForBreakfast%2ChasCatering%2ChasDelivery%2ChasDriveThru%2ChasMobileOrdering%2ChasParking%2ChasPlayground%2ChasWifi%2Clatitude%2Clongitude%2CmobileOrderingStatus%2Cnumber%2CparkingType%2CphoneNumber%2CphysicalAddress%2CplaygroundType%2Cpos%2CposRestaurantId%2CrestaurantPosData-%3E%7B_id%2C%20lastHeartbeatTimestamp%2C%20heartbeatStatus%7D%2Cstatus%2CrestaurantImage%7D&%24environment=%22prod%22&%24limit=4000&%24maxLat=55.08700072025173&%24maxLng=-65.1115781343339&%24minLat=24.863742777663404&%24minLng=-130.42717950774183&%24offset=0&%24status=%22Open%22&%24userLat=44.9754804&%24userLng=-93.26968599999998"
    r = session.get(url, headers=headers, stream=True, timeout=90)
    for item in json.loads(r.content)["result"]:
        store = item["_id"].replace("restaurant_", "")
        lat = item["latitude"]
        lng = item["longitude"]
        zc = item["physicalAddress"]["postalCode"]
        country = item["physicalAddress"]["country"][:2]
        state = item["physicalAddress"]["stateProvince"]
        city = item["physicalAddress"]["city"]
        add = (
            item["physicalAddress"]["address1"]
            + " "
            + item["physicalAddress"]["address2"]
        )
        add = add.strip().replace('"', "'")
        phone = item["phoneNumber"]
        typ = "Restaurant"
        website = "popeyes.com"
        purl = "<MISSING>"
        hours = "<MISSING>"
        name = "Popeye's"
        try:
            hours = (
                "Mon: "
                + item["deliveryHours"]["monOpen"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
                + "-"
                + item["deliveryHours"]["monClose"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Tue: "
                + item["deliveryHours"]["tueOpen"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
                + "-"
                + item["deliveryHours"]["tueClose"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Wed: "
                + item["deliveryHours"]["wedOpen"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
                + "-"
                + item["deliveryHours"]["wedClose"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Thu: "
                + item["deliveryHours"]["thrOpen"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
                + "-"
                + item["deliveryHours"]["thrClose"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Fri: "
                + item["deliveryHours"]["friOpen"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
                + "-"
                + item["deliveryHours"]["friClose"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Sat: "
                + item["deliveryHours"]["satOpen"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
                + "-"
                + item["deliveryHours"]["satClose"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Sun: "
                + item["deliveryHours"]["sunOpen"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
                + "-"
                + item["deliveryHours"]["sunClose"]
                .replace("1970-01-01 ", "")
                .rsplit(":", 1)[0]
            )
        except:
            pass
        if phone == "":
            phone = "<MISSING>"
        if "Required)" in add:
            add = add.split("Required)")[1].strip()
        if "Required)" in name:
            name = add.split("Required)")[1].strip()
        yield [
            website,
            purl,
            name,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
