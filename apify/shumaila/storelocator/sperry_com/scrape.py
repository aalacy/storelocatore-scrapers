from bs4 import BeautifulSoup
import csv
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
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


def settime(timenow, flag):
    if timenow == "0":
        return " Closed"
    st = (int)(timenow[0:2])
    if st > 12:
        st = st - 12
    zone = " AM - "
    if flag == 2:
        zone = " PM "
    return str(st) + ":" + timenow[2:4] + zone


def fetch_data():
    p = 0
    coordlist = static_coordinate_list(5, SearchableCountries.USA)
    data = []
    titlelist = []
    weeklist = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    for lat, lng in coordlist:
        url = (
            "https://sperry.locally.com/geo/point/"
            + str(lat)
            + "/"
            + str(lng)
            + "?switch_user_location=1"
        )
        r = session.get(url, headers=headers, verify=False).json()["nearest_stores"]
        try:
            idlist = r["ids"]
        except:
            continue
        loclist = r["data"]
        for pcode in idlist:
            loc = loclist[str(pcode)]
            store = loc["company_id"]
            title = loc["name"]
            city = loc["city"]
            state = loc["state"]
            street = loc["address"]
            lat = loc["lat"]
            longt = loc["lng"]
            phone = loc["phone"]
            ccode = loc["country"]
            if title in titlelist:
                continue
            titlelist.append(title)
            try:
                link = "https://www.sperry.com" + loc["base_url"]
                ltype = "Store"
            except:
                link = "https://www.sperry.com/en/content?caid=locally"
                ltype = "Dealer"
            hours = ""
            for day in weeklist:
                start = settime(str(loc[day + "_time_open"]), 1)
                if "Closed" in start:
                    end = " "
                else:
                    end = settime(str(loc[day + "_time_close"]), 2)
                hours = day + " " + start + end
            data.append(
                [
                    "https://www.sperry.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    ccode,
                    store,
                    phone,
                    ltype,
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
