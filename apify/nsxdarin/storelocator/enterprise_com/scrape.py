import csv
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt

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


@retry(stop=stop_after_attempt(7))
def get(loc):
    session = SgRequests()
    return session.get(loc, headers=headers)


def fetch_data():
    alllocs = []
    states = []
    url = "https://www.enterprise.com/en/car-rental/locations/us.html"
    r = get(url)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<h3 class="state-title"><a class="heading-link" href="' in line:
            lurl = "https://www.enterprise.com" + line.split('href="')[1].split('"')[0]
            states.append(lurl + "|US")
    url = "https://www.enterprise.com/en/car-rental/locations/canada.html"
    r = get(url)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<h3 class="state-title"><a class="heading-link" href="' in line:
            lurl = "https://www.enterprise.com" + line.split('href="')[1].split('"')[0]
            states.append(lurl + "|CA")
    for state in states:
        surl = state.split("|")[0]
        country = state.split("|")[1]
        locs = []
        r2 = get(surl)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a href="https://www.enterprise.com/en/car-rental/locations/' in line2:
                lurl = line2.split('href="')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    locs.append(lurl)
        for loc in locs:
            website = "enterprise.com"
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = ""
            phone = ""
            typ = "<MISSING>"
            lat = ""
            lng = ""
            hours = ""
            r3 = get(loc)
            for line3 in r3.iter_lines():
                line3 = str(line3.decode("utf-8"))
                if 'enterprise.locationDetail.locationmap.locationId = "' in line3:
                    store = line3.split(
                        'enterprise.locationDetail.locationmap.locationId = "'
                    )[1].split('"')[0]
                    surl = (
                        "https://prd-west.webapi.enterprise.com/enterprise-ewt/location/"
                        + store
                    )
                    r4 = get(surl)
                    for line4 in r4.iter_lines():
                        line4 = str(line4.decode("utf-8"))
                        if '"hours":[{"type":"STANDARD","days":[{' in line4:
                            days = (
                                line4.split('"hours":[{"type":"STANDARD","days":[{')[1]
                                .split("]}]},")[0]
                                .split('"day":"')
                            )
                            for day in days:
                                if '"date":"' in day:
                                    if '"closed_all_day":true' in day:
                                        hrs = day.split('"')[0] + ": Closed"
                                    else:
                                        hrs = (
                                            day.split('"')[0]
                                            + ": "
                                            + day.split('{"open_time":"')[1].split('"')[
                                                0
                                            ]
                                            + "-"
                                            + day.split('"close_time":"')[1].split('"')[
                                                0
                                            ]
                                        )
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                if '<meta property="og:title" content="' in line3:
                    name = (
                        line3.split('<meta property="og:title" content="')[1]
                        .split(" |")[0]
                        .replace("Car Rental ", "")
                    )
                if '"streetAddress" : "' in line3:
                    add = line3.split('"streetAddress" : "')[1].split('"')[0]
                if '"addressLocality" : "' in line3:
                    city = line3.split('"addressLocality" : "')[1].split('"')[0]
                if '"addressRegion" : "' in line3:
                    state = line3.split('"addressRegion" : "')[1].split('"')[0]
                if '"postalCode" : "' in line3:
                    zc = line3.split('"postalCode" : "')[1].split('"')[0]
                if '"telephone" : "' in line3:
                    phone = (
                        line3.split('"telephone" : "')[1].split('"')[0].replace("+", "")
                    )
                if '"latitude" : "' in line3:
                    lat = line3.split('"latitude" : "')[1].split('"')[0]
                if '"longitude" : "' in line3:
                    lng = line3.split('longitude" : "')[1].split('"')[0]
            if hours == "":
                hours = "<MISSING>"
            name = name.replace("&amp;", "&").replace("&#39;", "'")
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
