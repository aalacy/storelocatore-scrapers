from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
import csv
import json
import usaddress


logger = SgLogSetup().get_logger("penn-station_com")

session = SgRequests()

headers = {
    "authority": "www.penn-station.com",
    "method": "POST",
    "path": "/storefinder_responsive/index.php",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-length": "93",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "cookie": "__cfduid=de96e0a2e5390bad467365b1611157b821606368095; _ga=GA1.2.546990416.1606368118; _fbp=fb.1.1606368123314.1051536495; PHPSESSID=pqrqcqfooatri25lv7joohrb14; _gid=GA1.2.1113236853.1607666060",
    "origin": "https://www.penn-station.com",
    "referer": "https://www.penn-station.com/storefinder_responsive/embed.php",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

# All US states Coordinates
latlongdict = {
    0: ["32.3182314", "-86.902298"],
    1: ["33.416977", "-111.734779"],
    2: ["-14.270972", "-170.132217"],
    3: ["-14.270972", "-170.132217"],
    4: ["34.0489281", "-111.0937311"],
    5: ["35.20105", "-91.8318334"],
    6: ["36.778261", "-119.4179324"],
    7: ["39.5500507", "-105.7820674"],
    8: ["41.6032207", "-73.087749"],
    9: ["38.9108325", "-75.52766989999999"],
    10: ["34.0007104", "-81.0348144"],
    11: ["27.6648274", "-81.5157535"],
    12: ["32.1656221", "-82.9000751"],
    13: ["13.444304", "144.793731"],
    14: ["19.8967662", "-155.5827818"],
    15: ["44.0682019", "-114.7420408"],
    16: ["40.6331249", "-89.3985283"],
    17: ["40.2671941", "-86.1349019"],
    18: ["41.8780025", "-93.097702"],
    19: ["39.011902", "-98.4842465"],
    20: ["37.8393332", "-84.2700179"],
    21: ["30.9842977", "-91.96233269999999"],
    22: ["45.253783", "-69.4454689"],
    23: ["39.0457549", "-76.64127119999999"],
    24: ["42.4072107", "-71.3824374"],
    25: ["44.3148443", "-85.60236429999999"],
    26: ["46.729553", "-94.6858998"],
    27: ["32.3546679", "-89.3985283"],
    28: ["37.9642529", "-91.8318334"],
    29: ["46.8796822", "-110.3625658"],
    30: ["41.4925374", "-99.9018131"],
    31: ["38.8026097", "-116.419389"],
    32: ["43.1938516", "-71.5723953"],
    33: ["40.0583238", "-74.4056612"],
    34: ["34.5199402", "-105.8700901"],
    35: ["40.7127753", "-74.0059728"],
    36: ["35.7595731", "-79.01929969999999"],
    37: ["47.5514926", "-101.0020119"],
    38: ["15.0979", "145.6739"],
    39: ["40.4172871", "-82.90712300000001"],
    40: ["35.0077519", "-97.092877"],
    41: ["43.8041334", "-120.5542012"],
    42: ["41.2033216", "-77.1945247"],
    43: ["18.220833", "-66.590149"],
    44: ["41.5800945", "-71.4774291"],
    45: ["33.836081", "-81.1637245"],
    46: ["43.9695148", "-99.9018131"],
    47: ["35.5174913", "-86.5804473"],
    48: ["31.9685988", "-99.9018131"],
    49: ["39.3209801", "-111.0937311"],
    50: ["44.5588028", "-72.57784149999999"],
    51: ["18.335765", "-64.896335"],
    52: ["37.4315734", "-78.6568942"],
    53: ["47.7510741", "-120.7401385"],
    54: ["38.5976262", "-80.4549026"],
    55: ["43.7844397", "-88.7878678"],
    56: ["43.0759678", "-107.2902839"],
}


def write_output(data1):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        temp_list = []  # ignoring duplicates
        for row in data1:
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
    data1 = []
    for i in latlongdict:
        data = {
            "ajax": "1",
            "action": "get_nearby_stores",
            "distance": "100",
            "lat": latlongdict[i][0],
            "lng": latlongdict[i][1],
            "products": "1",
        }
        url = "https://www.penn-station.com/storefinder_responsive/index.php"
        r = session.post(url=url, data=data)
        api = r.text
        success = api.split('"success":', 1)[1].split(",")[0]
        if success == "1":
            loclist = api.split('"stores":')[1].split("]}", 1)[0]
            loclist = loclist + "]"
            loclist = json.loads(loclist)
            for loc in loclist:
                title = loc["name"]
                address = loc["address"]
                phone = loc["telephone"]
                if phone == "(614) 864-PENN (7366)":
                    phone = "(614) 864-7366"
                if phone == "":
                    phone = "<MISSING>"
                time = loc["description"]
                time = time.replace("\r\n", " ")
                if time == "":
                    time = "<MISSING>"
                time = time.lstrip()
                time = time.rstrip()
                time = time.lstrip('"')
                time = time.rstrip('"')
                time = time.lstrip()
                time = time.rstrip()
                time = time.replace("Mon-Sat:  ", "Mon - Sat: ")
                time = time.replace("Mon - Sat ", "Mon - Sat: ")
                time = time.replace("  ", " ")
                lat = loc["lat"]
                lngt = loc["lng"]
                address = address.replace(",", " ")
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

                data1.append(
                    [
                        "https://penn-station.com/locations.php",
                        url,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
                        "<MISSING>",
                        phone,
                        "<MISSING>",
                        lat,
                        lngt,
                        time,
                    ]
                )
    return data1


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data1 = fetch_data()
    write_output(data1)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
