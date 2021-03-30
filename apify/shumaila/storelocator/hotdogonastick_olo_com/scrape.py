import csv
import json
from sgrequests import SgRequests

session = SgRequests()

headerss = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "__requestverificationtoken": "zw5Apc8BinI_EXNOTNjMgeNY3MHBlXkDKef3k_U1_O2tfF6198pMYUp1nniIT5Un1fIlKyRpKMl8gOAUsPYVef9eHT01",
    "cookie": "__cfduid=d4b69d87dd23ea8e685266aa3467ed1ef1609240090; CT=O16G38gEYSB0O6fERgFkc9bw==R6Icy5mqN+jMFedriDZb9+JA4uUhz0F1wBglSjp/SeU=; _ga=GA1.3.1709778710.1609240098; _fbp=fb.1.1609240098132.1009375827; __RequestVerificationToken=j0GuvFZdfij2U2L5fljKCHZ1wbz_LXyML_cNxp3udpb6JrSHuU6rBd16NrhcY5gmbpgabmx4SVat_pjRfXVt4jvPenI1; ASP.NET_SessionId=lki2hfqdebezmfnxf10wxdv2; __cf_bm=19e0015f072bdfc42b334bcdffeeb36ae574c89c-1609607736-1800-AfH/O/Saz5oSu2iW3pfYtxF6rz+PYNkly28gDYJxjdYIMIEWBBkLj9oiN1PHIfq6hBEhOxMBXLsrI+03f8aFkbDi1rPWvDtJ29Knmkbri079tsXiwFeR8BUAECv31UpeNYM9lZqYI1EpIHlul3BJp8xl+Fi+dHF6M3zS5GcbpuRH; _gid=GA1.3.310121665.1609607742",
    "x-olo-request": "1",
    "x-olo-viewport": "Desktop",
    "x-requested-with": "XMLHttpRequest",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def fetch_data():
    data = []
    p = 0
    url = "https://hotdogonastick.olo.com/api/vendors/regions?excludeCities=true"
    statelist = session.get(url, headers=headerss, verify=False).json()
    for stnow in statelist:
        stlink = "https://hotdogonastick.olo.com/api/vendors/search/" + stnow["code"]
        loclist = session.get(stlink, headers=headerss, verify=False).json()[
            "vendor-search-results"
        ]
        for loc in loclist:
            store = loc["id"]
            title = loc["name"]
            link = "https://hotdogonastick.olo.com/menu/" + loc["slug"]
            phone = loc["phoneNumber"]
            phone = phone[1:4] + "-" + phone[4:7] + "-" + phone[7:11]
            street = loc["address"]["streetAddress"]
            city = loc["address"]["city"]
            state = loc["address"]["state"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            pcode = loc["address"]["postalCode"]
            hourslist = str(loc["weeklySchedule"]["calendars"][0]["schedule"]).replace(
                "'", '"'
            )
            hourslist = json.loads(str(hourslist))
            hours = ""
            for hr in hourslist:
                hours = hours + hr["weekDay"] + " : " + hr["description"] + " "
            if "See food truck" in street:
                continue
            data.append(
                [
                    "https://hotdogonastick.olo.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )

            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
