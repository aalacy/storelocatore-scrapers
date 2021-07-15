import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("allbirds_com")

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
    url = "https://www.allbirds.com/pages/stores"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    lines = r.iter_lines(decode_unicode=True)
    website = "allbirds.com"
    store = "<MISSING>"
    purl = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    typ = "Store"
    name = ""
    Intl = False
    for line in lines:
        if "Auckland" in line:
            Intl = True
        if '<h2 class="Typography--secondary-heading Typography--with-margin">' in line:
            name = line.split('">')[1].split("<")[0]
            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = ""
        if "see map</a></p>" in line.lower():
            murl = line.split('href="')[1].split('"')[0]
            r2 = session.get(murl, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            lat = r2.url.split("@")[1].split(",")[0]
            lng = r2.url.split("@")[1].split(",")[1]
        if "location</h3>" in line.lower():
            g = next(lines)
            h = next(lines)
            if "suite" in h.lower():
                h = next(lines)
            add = g.split('">')[1].split("<")[0].strip()
            city = h.split(",")[0].strip()
            try:
                state = h.split(",")[1].strip().split(" ")[0].strip()
            except:
                state = "<MISSING>"
            zc = h.split("<")[0].rsplit(" ", 1)[1].strip()
            if Intl is False:
                country = "US"
            else:
                country = "<MISSING>"
        if "day: " in line.lower() or "Saturday " in line:
            try:
                hrs = line.split('h">')[1].split("<")[0].strip()
            except:
                hrs = line.split("<")[0].strip()
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
        if "China" in line:
            country = "CN"
        if ", China" in line:
            zc = line.split(", China")[1].split("<")[0].strip()
        if ", Japan" in line:
            zc = line.split(", Japan")[1].split("<")[0].strip()
        if "Phone</h3>" in line:
            g = next(lines)
            phone = g.split('">')[1].split("<")[0].strip()
        if '<div class="StoresPageSection">' in line or '<div class="Footer">' in line:
            if name != "":
                logger.info(name)
                if name == "Austin":
                    add = "1011 S Congress Ave, Bldg 1, Ste. 120"
                    city = "Austin"
                    state = "TX"
                    zc = "78704"
                if "219 N 2nd" in add:
                    zc = "55401"
                if "Auckland" in name:
                    country = "NZ"
                if "London" in name:
                    country = "GB"
                if "Amsterdam" in name:
                    country = "NL"
                if "Tokyo" in name:
                    country = "JP"
                if "Berlin" in name:
                    country = "DE"
                if "Korea" in name:
                    country = "KR"
                if "<" in add:
                    add = add.split("<")[0]
                if country == "CN":
                    state = "<MISSING>"
                if "M39(B1MS-15)" in add:
                    zc = "610021"
                    add = "M39(B1MS-15) No. 8, Shamao St"
                    city = "Chengdu"
                if "SLG23" in add:
                    add = "SLG23 (South LG1, Unit 23) Nr. 19, Sanlitun Rd"
                    city = "Beijing"
                if "Harajuku" in name:
                    add = "1F Jingu No Mori Building, 1-14-34, Jungumae, Shibuya-ku"
                    city = "Tokyo"
                if "Marunouchi" in name:
                    add = "#105 Shin Kokusai Building, 3-4-1 Marunouchi, Chiyoda-ku"
                    city = "Tokyo"
                if "MU47a" in add:
                    add = "MU47a No.383 Tianhe Rd"
                    city = "Guangzhou"
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
