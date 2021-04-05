import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("appleone_com")


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


search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
    max_search_results=10,
)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Cookie": "statePreference=; statePreference=; preferredLocal=city=&countrycode=UK, GB&latitude=0&longitude=0; PretAManger-UK_Language=en-gb; _ga=GA1.3.682867871.1588958973; _gid=GA1.3.711697636.1588958973; _fbp=fb.2.1588958973219.1726351087; _y2=1%3AeyJjIjp7IjEyNDc2NiI6LTE0NzM5ODQwMDAsIjEyNTIxOCI6LTE0NzM5ODQwMDAsIjEyOTQ4NiI6LTE0NzM5ODQwMDAsIjEzMDIxNiI6LTE0NzM5ODQwMDAsIjEzMTc5NCI6LTE0NzM5ODQwMDAsIjEzMjUwOSI6LTE0NzM5ODQwMDAsIm8iOi0xNDczOTg0MDAwfX0%3D%3ALTE0NzEzNjMxNjg%3D%3A99; newsletterPageReferrer=https://www.pret.co.uk/en-gb/find-a-pret/London; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+08+2020+12%3A30%3A37+GMT-0500+(Central+Daylight+Time)&version=5.9.0&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_48371%3A1%2C0_48370%3A1%2C0_94508%3A1%2C0_94507%3A1%2C0_48372%3A1%2C0_48365%3A1%2C0_48367%3A1%2C0_48366%3A1%2C0_48369%3A1%2C0_48368%3A1%2C8%3A0&AwaitingReconsent=false; newsletterAction=dwell; newsletterDwellTime=56; _yi=1%3AeyJsaSI6bnVsbCwic2UiOnsiYyI6MSwibGEiOjE1ODg5NTkxMjEzNzgsInAiOjUsInNjIjoxMjN9LCJ1Ijp7ImlkIjoiZDA1MDIzNTctZWYxZC00OTlhLThmODAtOWIxMmI5MzVkYmVjIiwiZmwiOiIwIn19%3ALTE0MzE4NDYxMTI%3D%3A99; lastTimestamp=1588959122; preferredLocal=city=&countrycode=UK, GB&latitude=0&longitude=0; PretAManger-UK_Language=en-gb",
}


def fetch_data():
    ids = []
    EV = ""
    VSG = ""
    VS = ""
    url = "https://www.appleone.com/localoffice.aspx"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'name="__VIEWSTATE" id="__VIEWSTATE" value="' in line:
            VS = line.split('name="__VIEWSTATE" id="__VIEWSTATE" value="')[1].split(
                '"'
            )[0]
        if 'id="__VIEWSTATEGENERATOR" value="' in line:
            VSG = line.split('id="__VIEWSTATEGENERATOR" value="')[1].split('"')[0]
        if 'id="__EVENTVALIDATION" value="' in line:
            EV = line.split('id="__EVENTVALIDATION" value="')[1].split('"')[0]
    for zipcode in search:
        try:
            logger.info(("Pulling Postal Code %s..." % zipcode))
            headers2 = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                "Host": "www.appleone.com",
                "Origin": "https://www.appleone.com",
                "Referer": "https://www.appleone.com/localoffice.aspx",
            }
            payload = {
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": VS,
                "__VIEWSTATEGENERATOR": VSG,
                "__EVENTVALIDATION": EV,
                "ctl00$MainContentPlaceHolder$txtLocalZip": zipcode,
                "ctl00$MainContentPlaceHolder$txtLocalCity": "",
                "ctl00$MainContentPlaceHolder$ddlLocalState": "AK",
                "ctl00$MainContentPlaceHolder$btnSubmit": "Locate Offices",
            }
            r2 = session.post(url, headers=headers2, data=payload)
            lines = r2.iter_lines()
            website = "appleone.com"
            for line2 in lines:
                line2 = str(line2.decode("utf-8"))
                if '<dd class="accordion-navigation" data-officename="' in line2:
                    add = ""
                    city = ""
                    state = ""
                    loc = "<MISSING>"
                    zc = ""
                    country = "US"
                    phone = ""
                    typ = "<MISSING>"
                    store = "<MISSING>"
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    hours = ""
                    name = line2.split(
                        '<dd class="accordion-navigation" data-officename="'
                    )[1].split('"')[0]
                    addinfo = line2.split('address="')[1].split('"')[0]
                    if addinfo.count(",") == 3:
                        add = (
                            addinfo.split(",")[0] + " " + addinfo.split(",")[1].strip()
                        )
                        city = addinfo.split(",")[2].strip()
                        state = addinfo.split(",")[3].strip().split(" ")[0]
                        zc = addinfo.rsplit(" ", 1)[1]
                    else:
                        add = addinfo.split(",")[0]
                        city = addinfo.split(",")[1].strip()
                        state = addinfo.split(",")[2].strip().split(" ")[0]
                        zc = addinfo.rsplit(" ", 1)[1]
                if '<a href="tel:+' in line2:
                    phone = line2.split('">')[1].split("<")[0]
                if "day</span>" in line2:
                    day = line2.split(">")[1].split("<")[0]
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                    if ">" not in g:
                        g = next(lines)
                        g = str(g.decode("utf-8"))
                    hrs = day + ": " + g.split(">")[1].split("<")[0]
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
                if 'div id="gmap-display-' in line2:
                    info = name + "|" + add
                    if info not in ids:
                        ids.append(info)
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
