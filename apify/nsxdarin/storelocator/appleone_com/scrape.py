import csv
from sgzip.static import static_zipcode_list, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed

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


search = static_zipcode_list(10, SearchableCountries.USA)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Cookie": "_mkto_trk=id:815-TMY-864&token:_mch-appleone.com-1623683464541-85817; _ga=GA1.2.2031496430.1623683465; _fbp=fb.1.1623683464658.1694829143; OptanonAlertBoxClosed=2021-06-14T15:11:13.413Z; NSC_ofx_JEFW_xxx.bqqmfpof.dpn_iuuqt=ffffffff09cb1fa845525d5f4f58455e445a4a423660; _gid=GA1.2.813993892.1623857444; _gat_gtag_UA_3402201_1=1; OptanonConsent=isIABGlobal=false&datestamp=Wed+Jun+16+2021+10%3A31%3A29+GMT-0500+(Central+Daylight+Time)&version=5.12.0&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CBG1%3A1&hosts=&geolocation=US%3BMN&AwaitingReconsent=false",
}


def fetch_location(zipcode, EV, VSG, VS, ids, url):
    try:
        headers = {
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
        r = session.post(url, headers=headers, data=payload)
        lines = r.iter_lines()
        website = "appleone.com"

        for line in lines:
            line = str(line.decode("utf-8"))
            if '<dd class="accordion-navigation" data-officename="' in line:
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
                name = line.split('<dd class="accordion-navigation" data-officename="')[
                    1
                ].split('"')[0]
            if '<span class="addr-details">' in line:
                g = next(lines)
                h = next(lines)
                i = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                i = str(i.decode("utf-8"))
                add = g.split("<")[0].strip().replace("\t", "")
                try:
                    add = add + " " + h.split("<")[0].strip().replace("\t", "")
                except:
                    pass
                city = i.split(",")[0]
                state = i.split(",")[1].strip().split(" ")[0]
                zc = i.split("<")[0].strip().rsplit(" ", 1)[1]
            if '<a href="tel:+' in line:
                phone = line.split('">')[1].split("<")[0]
            if "day</span>" in line:
                day = line.split(">")[1].split("<")[0]
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
            if 'div id="gmap-display-' in line:
                city = city.strip().replace("\t", "")
                info = name + "|" + add
                if "10151 Deerwood Park Blvd" in add:
                    add = "10151 Deerwood Park Blvd Suite 110, Building 100"
                    city = "Jacksonville"
                    state = "FL"
                    zc = "32256"
                if info not in ids:
                    ids.append(info)
                    return [
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
    except Exception as e:
        logger.error(e)


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

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_location, zipcode, EV, VSG, VS, ids, url)
            for zipcode in search
        ]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
