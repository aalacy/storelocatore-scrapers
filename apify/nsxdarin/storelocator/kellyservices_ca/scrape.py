import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("kellyservices_ca")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=None,
    max_search_results=25,
)


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
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
    url = "https://branchlocator.kellyservices.com/default.aspx"
    r = session.get(url, headers=headers)
    VS = ""
    VSG = ""
    EV = ""
    ids = []
    for line in r.iter_lines(decode_unicode=True):
        if 'type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="' in line:
            VS = line.split(
                'type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="'
            )[1].split('"')[0]
        if (
            'type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="'
            in line
        ):
            VSG = line.split(
                'type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="'
            )[1].split('"')[0]
        if (
            'type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="'
            in line
        ):
            EV = line.split(
                'type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="'
            )[1].split('"')[0]
    for code in search:
        logger.info(code)
        url = "https://branchlocator.kellyservices.com/default.aspx"
        headers2 = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        }
        payload = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": VS,
            "__VIEWSTATEGENERATOR": VSG,
            "__EVENTVALIDATION": EV,
            "ddlInLanguage": "1",
            "txtLanguage": "1",
            "txtSecondaryLanguage": "1",
            "txtPrimaryLanguage": "1",
            "ddlBranchTypes": "15",
            "txtZip": code + "1A1",
            "txtCity": "",
            "ddlStates": "AL",
            "btnSearch": "Search",
            "txtServiceLine": "0",
            "txtDisplayMode": "expanded",
        }
        r2 = session.post(url, headers=headers2, data=payload)
        lines = r2.iter_lines(decode_unicode=True)
        website = "kellyservices.ca"
        typ = "Branch"
        name = ""
        country = ""
        for line2 in lines:
            if '<td align="center" valign="top" width="135px">' in line2:
                add = ""
                city = ""
                state = ""
                zc = ""
                phone = ""
                lat = ""
                lng = ""
                next(lines)
                store = (
                    next(lines)
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\t", "")
                    .strip()
                )
            if '<td align="left" valign="top" width="400px">' in line2:
                next(lines)
                name = (
                    next(lines)
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\t", "")
                    .strip()
                )
                if '<font color="' in name:
                    name = (
                        next(lines)
                        .replace("\t", "")
                        .replace("\r", "")
                        .replace("\t", "")
                        .strip()
                    )
            if "&sll=" in line2:
                lat = line2.split("&sll=")[1].split(",")[0]
                lng = line2.split("&sll=")[1].split(",")[1].split("'")[0]
            if 'Expanded" style="width:235px;">' in line2:
                addfull = (
                    line2.split('Expanded" style="width:235px;">')[1]
                    .split("</span>")[0]
                    .replace("<br><br>", "<br>")
                )
                hours = "<MISSING>"
                if "(Phone)" in addfull:
                    phone = addfull.split("&nbsp;(Phone)")[0].rsplit(">", 1)[1]
                else:
                    phone = "<MISSING>"
                items = addfull.split("<br>")
                SFound = False
                if ", " in addfull:
                    for item in items:
                        if ", " in item:
                            SFound = True
                            city = item.split(",")[0]
                            state = item.split(",")[1].strip().split(" ")[0]
                            try:
                                zc = item.split(",")[1].strip().split(" ", 1)[1]
                            except:
                                zc = "<MISSING>"
                        if SFound is False:
                            if add == "":
                                add = item
                            else:
                                add = add + " " + item
                else:
                    add = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zc = "<MISSING>"
                if add == "":
                    add = "<MISSING>"
                if lat == "0":
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                if " " in zc:
                    country = "CA"
                else:
                    country = "US"
                if store not in ids and store != "" and country == "CA":
                    ids.append(store)
                    yield [
                        website,
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
