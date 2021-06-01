import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("aldoshoes_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "x-aldo-brand": "aldoshoes",
    "x-aldo-region": "us",
    "x-aldo-ssr-request-id": "",
    "x-aldo-lang": "en_US",
    "x-forwarded-akamai-edgescape": "undefined",
    "x-aldo-api-version": "2",
}

caheaders = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "x-aldo-brand": "aldoshoes",
    "x-aldo-region": "ca",
    "x-aldo-ssr-request-id": "",
    "x-aldo-lang": "en_US",
    "x-forwarded-akamai-edgescape": "undefined",
    "x-aldo-api-version": "2",
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
    for x in range(2000, 3000):
        surl = "https://www.aldoshoes.com/us/en_US/store-locator/store/" + str(x)
        r2 = session.get(surl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        name = ""
        add = ""
        typ = "Store"
        city = ""
        state = ""
        zc = ""
        country = "US"
        website = "aldoshoes.com"
        lat = ""
        lng = ""
        hours = ""
        phone = ""
        logger.info(("%s..." % str(x)))
        SFound = False
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<title data-react-helmet="true">' in line2:
                name = line2.split('<title data-react-helmet="true">')[1].split(" |")[0]
            if 'span class="c-markdown">Store details</span>' in line2:
                SFound = True
            if '"line1":"' in line2:
                add = line2.split('"line1":"')[1].split('"')[0]
                try:
                    state = (
                        line2.split(',"isocodeShort":"')[1]
                        .split('"name":"')[1]
                        .split('"')[0]
                    )
                except:
                    state = "PR"
                city = line2.split('"town":"')[1].split('"')[0]
                try:
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                except:
                    zc = "<MISSING>"
                store = line2.split('},"name":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
                days = (
                    line2.split('"weekDayOpeningList":[{')[1]
                    .split('},"shipToStore":')[0]
                    .split('"},{"')
                )
                hours = ""
                for day in days:
                    if '"weekDay":"' in day:
                        dname = day.split('"weekDay":"')[1].split('"')[0]
                        if 'closed":true' in day:
                            hrs = "Closed"
                        else:
                            hrs = (
                                day.split('openingTime":{"formattedHour":"')[1].split(
                                    '"'
                                )[0]
                                + "-"
                                + day.split('closingTime":{"formattedHour":"')[1].split(
                                    '"'
                                )[0]
                            )
                        if hours == "":
                            hours = dname + ": " + hrs
                        else:
                            hours = hours + "; " + dname + ": " + hrs
        if SFound:
            yield [
                website,
                surl,
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

    url = "https://www.aldoshoes.com/api/stores?countryCode=US&lat=44.99512980000001&lng=-93.4352207&allStores=True"
    rcan = session.get(url, headers=caheaders)
    for item in json.loads(rcan.content)["stores"]:
        add = item["address"]["line1"]
        city = item["address"]["town"]
        zc = item["address"]["postalCode"]
        country = "CA"
        website = "aldoshoes.com"
        name = item["displayName"]
        state = item["address"]["region"]["name"]
        lat = item["geoPoint"]["latitude"]
        lng = item["geoPoint"]["longitude"]
        store = item["name"]
        purl = "https://www.aldoshoes.com/ca/en/store-locator/store/" + store
        typ = "Store"
        try:
            phone = item["address"]["phone"]
        except:
            phone = "<MISSING>"
        days = item["openingHours"]["weekDayOpeningList"]
        hours = ""
        for day in days:
            dname = day["weekDay"]
            try:
                ot = day["openingTime"]["formattedHour"]
            except:
                ot = ""
            try:
                ct = day["closingTime"]["formattedHour"]
            except:
                ct = ""
            if ct == "":
                hrs = "Closed"
            else:
                hrs = ot + "-" + ct
            if hours == "":
                hours = dname + ": " + hrs
            else:
                hours = hours + "; " + dname + ": " + hrs
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
