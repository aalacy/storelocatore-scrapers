import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("onehourheatandair_com")


session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
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
    url = "https://www.onehourheatandair.com/locations/"
    locs = []
    payload = {"_m_": "LocationList"}
    r = session.post(url, headers=headers, data=payload)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "View Website</a>" in line:
            locs.append(
                "https://www.onehourheatandair.com"
                + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "onehourheatandair.com"
        name = ""
        country = "US"
        lat = "<MISSING>"
        lng = "<MISSING>"
        typ = "Location"
        store = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        hours = "<MISSING>"
        phone = "<MISSING>"
        zc = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        add = "<MISSING>"
        add2 = "<MISSING>"
        for line2 in lines:
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
            if '<meta itemprop="longitude" content="' in line2:
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if (
                '<a class="color-swap social-link" href="https://www.google.com/maps/place/'
                in line2
            ):
                try:
                    add2 = line2.split("2s")[1].split(",")[0].replace("+", " ")
                except:
                    add2 = "<MISSING>"
            if '<span itemprop="streetAddress">' in line2:
                g = next(lines)
                add = g.replace("\r", "").replace("\t", "").replace("\n", "").strip()
            if '<span itemprop="postalCode">' in line2:
                zc = line2.split('<span itemprop="postalCode">')[1].split("<")[0]
            if "<title>" in line2:
                name = line2.split(">")[1].split(" |")[0]
            if '<span class="flex-middle margin-right-tiny">' in line2:
                city = line2.split('<span class="flex-middle margin-right-tiny">')[
                    1
                ].split(",")[0]
                state = (
                    line2.split('<span class="flex-middle margin-right-tiny">')[1]
                    .split("<")[0]
                    .rsplit(" ", 1)[1]
                )
            if (
                '<a class="phone-link phone-number-style text-color" href="tel:'
                in line2
            ):
                phone = line2.split(
                    '<a class="phone-link phone-number-style text-color" href="tel:'
                )[1].split('"')[0]
        if name != "":
            if add == "<MISSING>":
                add = add2
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
