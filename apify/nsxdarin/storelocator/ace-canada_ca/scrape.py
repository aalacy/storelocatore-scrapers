import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Host": "www.ace-canada.ca",
    "Origin": "https://www.ace-canada.ca",
    "Referer": "https://www.ace-canada.ca/store-locator.aspx",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}

logger = SgLogSetup().get_logger("ace-canada_ca")


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
    url = "https://www.ace-canada.ca/store-locator.aspx"
    r = session.get(url, headers=headers)
    states = ["AB", "BC", "MB", "NB", "NT", "ON", "QC", "SK"]
    VS = ""
    VSG = ""
    country = "CA"
    cities = []
    website = "ace-canada.ca"
    store = "<MISSING>"
    ids = []
    typ = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'name="__VIEWSTATE" id="__VIEWSTATE" value="' in line:
            VS = line.split('name="__VIEWSTATE" id="__VIEWSTATE" value="')[1].split(
                '"'
            )[0]
        if 'id="__VIEWSTATEGENERATOR" value="' in line:
            VSG = line.split('id="__VIEWSTATEGENERATOR" value="')[1].split('"')[0]
    for state in states:
        logger.info(state)
        payload = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": VS,
            "__VIEWSTATEGENERATOR": VSG,
            "ctl00$ctl00$NestedMaster$PageHeader$StoreHeader_H$SimpleSearch1$hdSearchPhrase": "",
            "q": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$hdnLatitude": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$hdnLongitude": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$hdnSearchType": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$ddlProvince": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$ddl_province": state,
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$ddl_city": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$PostalCodeTextBox": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$RadiusList": "200",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$PostalGo.x": "36",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$PostalGo.y": "10",
        }
        r2 = session.post(url, headers=headers, data=payload)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<option value="' in line2:
                val = line2.split('value="')[1].split('"')[0]
                if val not in states and val != "" and val != "50" and val != "100":
                    cities.append(state + "|" + val)
            if 'name="__VIEWSTATE" id="__VIEWSTATE" value="' in line2:
                VS = line2.split('name="__VIEWSTATE" id="__VIEWSTATE" value="')[
                    1
                ].split('"')[0]
            if 'id="__VIEWSTATEGENERATOR" value="' in line2:
                VSG = line2.split('id="__VIEWSTATEGENERATOR" value="')[1].split('"')[0]
    for city in cities:
        logger.info(city)
        pname = city.split("|")[0]
        cname = city.split("|")[1]
        payload2 = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": VS,
            "__VIEWSTATEGENERATOR": VSG,
            "ctl00$ctl00$NestedMaster$PageHeader$StoreHeader_H$SimpleSearch1$hdSearchPhrase:": "",
            "q": "",
            "ctl00$ctl00$NestedMaster$PageHeader$StoreHeader_H$storeNav$SimpleSearch1$hdSearchPhrase": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$hdnLatitude": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$hdnLongitude": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$hdnSearchType": "PROVINCE_CITY",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$ddlProvince": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$ddl_province": pname,
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$ddl_city": cname,
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$PostalCodeTextBox": "",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$RadiusList": "50",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$CityProvGO.x": "15",
            "ctl00$ctl00$NestedMaster$PageContent$ctl00$CityProvGO.y": "16",
        }
        r2 = session.post(url, headers=headers, data=payload2)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if 'name="__VIEWSTATE" id="__VIEWSTATE" value="' in line2:
                VS = line2.split('name="__VIEWSTATE" id="__VIEWSTATE" value="')[
                    1
                ].split('"')[0]
            if 'id="__VIEWSTATEGENERATOR" value="' in line2:
                VSG = line2.split('id="__VIEWSTATEGENERATOR" value="')[1].split('"')[0]
            if 'NameLabel">' in line2:
                name = line2.split('NameLabel">')[1].split("<")[0]
                add = ""
                city = ""
                state = ""
                lat = ""
                zc = ""
                lng = ""
                hours = ""
                phone = ""
            if 'AddressLabel">' in line2:
                add = line2.split('AddressLabel">')[1].split("<")[0]
            if 'CityLabel">' in line2:
                city = line2.split('CityLabel">')[1].split("<")[0]
                state = line2.split('_ProvLabel">')[1].split("<")[0]
            if '_PostLabel">' in line2:
                zc = line2.split('_PostLabel">')[1].split("<")[0]
            if 'PhoneLabel">' in line2:
                phone = line2.split('PhoneLabel">')[1].split("<")[0]
            if "<!--" in line2 and "code" not in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                lat = g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
                g = next(lines)
                g = str(g.decode("utf-8"))
                lng = g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
            if "class='stday'>" in line2:
                hrs = (
                    line2.split("class='stday'>")[1].split("<")[0]
                    + ": "
                    + line2.split("</span>")[1].split("<")[0].strip()
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "https://maps.google.com" in line2:
                loc = "<MISSING>"
                addinfo = add + "|" + city + "|" + zc
                if addinfo not in ids:
                    ids.append(addinfo)
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
