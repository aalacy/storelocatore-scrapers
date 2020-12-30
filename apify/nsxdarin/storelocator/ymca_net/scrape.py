import csv
from sgrequests import SgRequests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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
    for x in range(1, 5000):
        print(str(x))
        try:
            session = SgRequests()
            url = "https://www.ymca.net/y-profile/?id=" + str(x)
            page_text = session.get(url, headers=headers)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            phone = ""
            website = "ymca.net"
            typ = "<MISSING>"
            country = "US"
            loc = url
            store = str(x.decode("utf-8"))
            hours = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            AFound = False
            for line in page_text:
                line = str(line.decode("utf-8"))
                if "<h1>" in line and name == "":
                    name = line.split("<h1>")[1].split("</h1>")[0]
                if "Set as default Y" in line:
                    while AFound is False:
                        g = next(page_text)
                        g = str(g.decode("utf-8"))
                        if "<br />" in g:
                            AFound = True
                            add = g.split("<")[0].strip().replace("\t", "")
                            g = next(page_text)
                            g = str(g.decode("utf-8"))
                            if g.count("<br />") == 2:
                                add = (
                                    add
                                    + " "
                                    + g.split("<br />")[0].strip().replace("\t", "")
                                )
                                csz = g.split("<br />")[1].strip().replace("\t", "")
                            else:
                                csz = g.split("<br />")[0].strip().replace("\t", "")
                            city = csz.split(",")[0]
                            state = csz.split(",")[1].strip().split(" ")[0]
                            zc = csz.rsplit(" ", 1)[1]
                if "Phone:" in line:
                    phone = line.split("Phone:")[1].split("<")[0].strip()
                if 'data-latitude="' in line:
                    lat = line.split('data-latitude="')[1].split('"')[0]
                if 'data-longitude"' in line:
                    lng = line.split('data-longitude="')[1].split('"')[0]
                if "ay: " in line and " - " in line and "<br />" in line:
                    hrs = line.split("<")[0].strip().replace("\t", "")
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if name != "":
                if hours == "":
                    hours = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
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
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
