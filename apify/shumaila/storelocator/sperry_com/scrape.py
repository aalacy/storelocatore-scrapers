from bs4 import BeautifulSoup
import csv

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
    endt = "00"
    if timenow == "0":
        return " Closed"
    if len(timenow) == 3:
        st = (int)(timenow[0:1])
        endt = timenow[1:3]
    elif len(timenow) == 4:
        st = (int)(timenow[0:2])
        endt = timenow[2:4]
    if st > 12:
        st = st - 12
    zone = " AM - "
    if flag == 2:
        zone = " PM "
    return str(st) + ":" + endt + zone


def fetch_data():
    p = 0
    data = []
    titlelist = []
    weeklist = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    url = "https://sperry.locally.com/stores/conversion_data?has_data=true&company_id=1566&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=40.73218673716792&map_center_lng=-73.98935000000014&map_distance_diag=5000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=.json"
    loclist = session.get(url, headers=headers, verify=False).json()["markers"]

    for loc in loclist:

        store = loc["id"]
        title = loc["name"]
        city = loc["city"]
        state = loc["state"]
        street = loc["address"]
        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["phone"]
        ccode = loc["country"]
        pcode = loc["zip"]
        if title in titlelist:
            continue
        titlelist.append(title)
        if "Sperry" in title:
            ltype = "Store"
        else:
            ltype = "Dealer"
        link = "https://www.sperry.com/en/content?caid=locally"

        hours = ""
        try:
            for day in weeklist:

                start = settime(str(loc[day + "_time_open"]), 1)
                if "Closed" in start:
                    end = " "
                else:
                    end = settime(str(loc[day + "_time_close"]), 2)
                hours = hours + day + " " + start + end
        except:
            hours = "<MISSING>"
        if len(phone) < 3:
            phone = "<MISSING>"
        if "mon  Closed" in hours and "tue  Closed" in hours:
            hours = "Mon-Sun Closed"
        data.append(
            [
                "https://www.sperry.com/",
                link,
                title.replace("\u010d", " ")
                .replace("\u200b", " ")
                .replace("\u200e", "")
                .strip(),
                street.replace("\u010d", " ").replace("\u200b", " ").strip(),
                city.replace("\u010d", " ").replace("\u200b", " ").strip(),
                state.replace("\u010d", " ").replace("\u200b", " ").strip(),
                pcode,
                ccode.replace("\u010d", " ").replace("\u200b", " ").strip(),
                store,
                phone.replace("\u010d", " ").replace("\u200b", " ").strip(),
                ltype.replace("\u010d", " ").replace("\u200b", " ").strip(),
                lat.replace("\u010d", " ").replace("\u200b", " ").strip(),
                longt.replace("\u010d", " ").replace("\u200b", " ").strip(),
                hours.replace("\u010d", " ").replace("\u200b", " ").strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
