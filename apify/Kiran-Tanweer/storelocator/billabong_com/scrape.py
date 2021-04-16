import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress

logger = SgLogSetup().get_logger("billabong_com")

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
}

coordinates = {
    0: ["40.71304702758789", "-74.00723266601562"],
    1: ["28.59551239013672", "-82.48734283447266"],
    2: ["37.25467300415039", "-119.61727905273438"],
    3: ["31.46379280090332", "-99.3332748413086"],
    4: ["40.896697998046875", "-77.83889770507812"],
    5: ["32.64828872680664", "-83.44437408447266"],
    6: ["64.14453887939453", "-152.28460693359375"],
    7: ["34.29323959350586", "-111.66461944580078"],
    8: ["44.87479782104492", "-85.7309799194336"],
    9: ["38.89206314086914", "-77.01991271972656"],
    10: ["39.356468200683594", "-116.65540313720703"],
    11: ["19.610876083374023", "-155.52749633789062"],
    12: ["42.17235565185547", "-71.6050033569336"],
    13: ["40.41553497314453", "-82.70935821533203"],
    14: ["35.58344650268555", "-97.50830078125"],
    15: ["44.639957427978516", "-89.73297882080078"],
    16: ["32.76642608642578", "-86.84033203125"],
    17: ["38.99855041503906", "-105.5478286743164"],
    18: ["35.53937530517578", "-79.18543243408203"],
    19: ["47.03351974487305", "-109.64512634277344"],
    20: ["39.91999053955078", "-86.28179931640625"],
    21: ["40.139095306396484", "-74.67851257324219"],
    22: ["40.124141693115234", "-89.14862823486328"],
    23: ["37.51290512084961", "-78.69762420654297"],
    24: ["31.314050674438477", "-83.9100112915039"],
    25: ["43.938682556152344", "-120.55810546875"],
    26: ["45.346641540527344", "-69.21614074707031"],
    27: ["39.008758544921875", "-75.46864318847656"],
    28: ["38.952735900878906", "-76.7012939453125"],
    29: ["39.32377624511719", "-111.67822265625"],
    30: ["38.36750030517578", "-92.47724151611328"],
    31: ["35.84299087524414", "-86.34325408935547"],
    32: ["37.52732849121094", "-85.2877197265625"],
    33: ["30.981019973754883", "-91.89180755615234"],
    34: ["41.57515335083008", "-72.73828125"],
    35: ["38.4847297668457", "-98.38018035888672"],
    36: ["42.99962615966797", "-107.55145263671875"],
    37: ["33.903934478759766", "-80.89408111572266"],
    38: ["34.42136764526367", "-106.10839080810547"],
    39: ["34.899803161621094", "-92.43915557861328"],
    40: ["42.07465744018555", "-93.50006103515625"],
    41: ["41.527103424072266", "-99.81059265136719"],
    42: ["32.72087478637695", "-89.65614318847656"],
    43: ["44.38907241821289", "-114.65937042236328"],
    44: ["44.075252532958984", "-72.6626968383789"],
    45: ["47.44630813598633", "-100.46932220458984"],
    46: ["41.628292083740234", "-71.51880645751953"],
    47: ["43.68561935424805", "-71.57763671875"],
    48: ["38.642574310302734", "-80.61373901367188"],
    49: ["44.4361457824707", "-100.23049926757812"],
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    for i in range(0, len(coordinates)):
        url = (
            "https://www.billabong.com/on/demandware.store/Sites-BB-US-Site/en_US/StoreLocator-StoreLookup?latitude="
            + coordinates[i][0]
            + "&longitude="
            + coordinates[i][1]
            + "&mapRadius=1000&filterBBStores=true&filterBBRetailers=false"
        )
        r = session.post(url, headers=headers, verify=False).json()
        for store in r["stores"]:
            country = store["country"].strip()
            if country == "US":
                storeid = store["ID"].strip()
                title = store["name"].strip()
                address = store["address"].strip()
                latitude = store["latitude"]
                latitude = str(latitude)
                longitude = store["longitude"]
                longitude = str(longitude)
                phone = store["phone"]
                if phone is None:
                    phone = "<MISSING>"
                else:
                    phone = phone.strip()
                address = address.replace("Orlando", "Orlando ")
                address = address.replace("  ", " ")
                address = address.replace(",", "")
                address = address.replace("Fl.", "FL")
                address = usaddress.parse(address)

                i = 0
                street = ""
                city = ""
                state = ""
                pcode = ""
                while i < len(address):
                    temp = address[i]
                    if (
                        temp[1].find("Address") != -1
                        or temp[1].find("Street") != -1
                        or temp[1].find("Recipient") != -1
                        or temp[1].find("Occupancy") != -1
                        or temp[1].find("BuildingName") != -1
                        or temp[1].find("USPSBoxType") != -1
                        or temp[1].find("USPSBoxID") != -1
                    ):
                        street = street + " " + temp[0]
                    if temp[1].find("PlaceName") != -1:
                        city = city + " " + temp[0]
                    if temp[1].find("StateName") != -1:
                        state = state + " " + temp[0]
                    if temp[1].find("ZipCode") != -1:
                        pcode = pcode + " " + temp[0]
                    i += 1
                street = street.lstrip()
                street = street.replace(",", "")
                city = city.lstrip()
                city = city.replace(",", "")
                state = state.lstrip()
                state = state.replace(",", "")
                pcode = pcode.lstrip()
                pcode = pcode.replace(",", "")

                hours = store["storeHours"]

                hrs = ""
                for hour in hours:
                    day = hour[0]
                    open_time = hour[1]
                    if hour[3] is None:
                        close_time = hour[4]
                    else:
                        close_time = hour[3]
                    hoo = day + ": " + str(open_time) + "-" + str(close_time) + " "
                    hrs = hoo + hrs
                hours = hrs
                hours = hours.strip()

                if street == "121 Waterworks Way":
                    city = store["city"]
                    pcode = store["postalCode"]
                    state = "<MISSING>"
                if street == "555 Shops at Mission Viejo":
                    city = store["city"]
                    pcode = store["postalCode"]
                    state = "<MISSING>"
                data.append(
                    [
                        "https://www.billabong.com/",
                        "https://www.billabong.com/stores/",
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        country,
                        storeid,
                        phone,
                        "Store",
                        latitude,
                        longitude,
                        hours,
                    ]
                )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
