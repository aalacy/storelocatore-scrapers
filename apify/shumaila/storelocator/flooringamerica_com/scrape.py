import csv
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

headers1 = {
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "__utmz=228289738.1607712791.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.1765622659.1607712791; _fbp=fb.1.1607712791920.1788469926; _hjid=314b33cd-fa75-4f72-8e84-4e51315ec0d3; __utmc=228289738; _gid=GA1.2.1597280948.1607864983; _hjTLDTest=1; utmAdditionalValues=city=tuscaloosa; __utma=228289738.1765622659.1607712791.1607864982.1607870721.7; __utmt=1; _gat_UA-6452490-3=1; _gat_UA-154777885-1=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample=1; __utmb=228289738.3.10.1607870721; _uetsid=774721803d4411eb8deaf352760bbd2f; _uetvid=1daee3f03be211eba45e3f6328b1b447",
    "Referer": "https://www.flooringamerica.com/states/alaska",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
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
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    for st in states:
        url = "https://www.flooringamerica.com/api/enterprise/franchisees/bycitystate"

        myobj = {"BrandId": 2, "State": st}
        loclist = session.post(url, headers=headers1, data=myobj, verify=False).json()

        for loc in loclist:

            title = loc["LocationName"]
            street = loc["Line1"]
            try:
                if len(loc["Line2"]):
                    street = street + " " + loc["Line2"]
            except:
                pass
            city = loc["City"]
            state = loc["State"]
            pcode = loc["Postal"]
            phone = loc["OrganicLocal"]
            lat = loc["Latitude"]
            longt = loc["Longitude"]
            store = loc["LocationNumber"]
            link = loc["MicroSiteUrl"]
            hours = ""
            try:
                avlink = link + "/about"
                avlink = avlink.replace("//about", "/about")
                r = session.get(avlink, headers=headers, verify=False, timeout=10)
                hourlist = r.text.split("var data = ", 1)[1].split("}]", 1)[0]
                hourlist = json.loads(hourlist + "}]")

                for hr in hourlist:
                    try:
                        hours = (
                            hours
                            + hr["DayOfWeek"]
                            + " "
                            + hr["OpenTime"].split(" ", 1)[1]
                            + " - "
                            + hr["CloseTime"].split(" ", 1)[1]
                            + " "
                        )
                    except:
                        hours = hours + hr["DayOfWeek"] + " Closed "
            except:
                hours = "<MISSING>"
            try:
                if len(phone) < 3:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"
            data.append(
                [
                    "https://www.flooringamerica.com",
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
