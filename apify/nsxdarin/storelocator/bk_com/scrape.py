import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bk_com")


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
    url = "https://czqk28jt.apicdn.sanity.io/v1/data/query/prod_bk?query=*%5B%20_type%20%3D%3D%20%27restaurant%27%20%26%26%20environment%20%3D%3D%20%24environment%20%26%26%20!(%24appEnvironemnt%20in%20coalesce(hideInEnvironments%2C%20%5B%5D))%20%26%26%20latitude%20%3E%20%24minLat%20%26%26%20latitude%20%3C%20%24maxLat%20%26%26%20longitude%20%3E%20%24minLng%20%26%26%20longitude%20%3C%20%24maxLng%20%26%26%20status%20%3D%3D%20%24status%20%5D%20%7Corder((%24userLat%20-%20latitude)%20**%202%20%2B%20(%24userLng%20-%20longitude)%20**%202)%5B%24offset...(%24offset%20%2B%20%24limit)%5D%20%7B_id%2CdeliveryHours%2CdiningRoomHours%2CcurbsideHours%2CdrinkStationType%2CdriveThruHours%2CdriveThruLaneType%2Cemail%2CfranchiseGroupId%2CfranchiseGroupName%2CfrontCounterClosed%2ChasBreakfast%2ChasBurgersForBreakfast%2ChasCurbside%2ChasDineIn%2ChasCatering%2ChasDelivery%2ChasDriveThru%2ChasMobileOrdering%2ChasParking%2ChasPlayground%2ChasTakeOut%2ChasWifi%2Clatitude%2Clongitude%2CmobileOrderingStatus%2Cname%2Cnumber%2CparkingType%2CphoneNumber%2CphysicalAddress%2CplaygroundType%2Cpos%2CposRestaurantId%2CrestaurantPosData-%3E%7B_id%2C%20lastHeartbeatTimestamp%2C%20heartbeatStatus%2C%20heartbeatOverride%7D%2Cstatus%2CrestaurantImage%7B...%2C%20asset-%3E%7D%7D&%24appEnvironemnt=%22prod%22&%24environment=%22prod%22&%24limit=20000&%24maxLat=70.763572273060035&%24maxLng=-60.93888052235278&%24minLat=10.661939543337255&%24minLng=-170.07296274481037&%24offset=0&%24status=%22Open%22&%24userLat=40.7127753&%24userLng=-74.0059728"
    Found = False
    while Found is False:
        logger.info("Getting Locations...")
        r = session.get(url, headers=headers, timeout=150, stream=True)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"_id":"restaurant_' in line:
                Found = True
                items = line.split('"_id":"restaurant_')
                for item in items:
                    if '"curbsideHours":' in item:
                        website = "bk.com"
                        typ = "<MISSING>"
                        store = item.split('"')[0]
                        loc = (
                            "https://www.bk.com/store-locator/store/restaurant_" + store
                        )
                        country = "US"
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        try:
                            phone = item.split('"phoneNumber":"')[1].split('"')[0]
                        except:
                            phone = "<MISSING>"
                        add = (
                            item.split('"address1":"')[1].split('"')[0]
                            + " "
                            + item.split('"address2":"')[1].split('"')[0]
                        )
                        add = add.strip()
                        add = add
                        city = item.split('"city":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        state = item.split('"stateProvinceShort":"')[1].split('"')[0]
                        days = item.split(
                            '"diningRoomHours":{"_type":"hoursOfOperation"'
                        )[1].split("}")[0]
                        hours = ""
                        try:
                            hours = (
                                "Mon: "
                                + days.split('"monOpen":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                                + "-"
                                + days.split('"monClose":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                            )
                        except:
                            pass
                        try:
                            hours = (
                                hours
                                + "; Tue: "
                                + days.split('"tueOpen":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                                + "-"
                                + days.split('"tueClose":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                            )
                        except:
                            pass
                        try:
                            hours = (
                                hours
                                + "; Wed: "
                                + days.split('"wedOpen":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                                + "-"
                                + days.split('"wedClose":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                            )
                        except:
                            pass
                        try:
                            hours = (
                                hours
                                + "; Thu: "
                                + days.split('"thrOpen":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                                + "-"
                                + days.split('"thrClose":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                            )
                        except:
                            pass
                        try:
                            hours = (
                                hours
                                + "; Fri: "
                                + days.split('"friOpen":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                                + "-"
                                + days.split('"friClose":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                            )
                        except:
                            pass
                        try:
                            hours = (
                                hours
                                + "; Sat: "
                                + days.split('"satOpen":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                                + "-"
                                + days.split('"satClose":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                            )
                        except:
                            pass
                        try:
                            hours = (
                                hours
                                + "; Sun: "
                                + days.split('"sunOpen":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                                + "-"
                                + days.split('"sunClose":"')[1]
                                .split(':00"')[0]
                                .split(" ")[1]
                            )
                        except:
                            pass
                        if hours == "":
                            hours = "<MISSING>"
                        phone = phone.encode("ascii", errors="ignore").decode()
                        if phone == "":
                            phone = "<MISSING>"
                        if '"diningRoomHours":{"_type":"hoursOfOperation"}' in item:
                            hours = "Sun-Sat: Closed"
                        yield [
                            website,
                            loc,
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
