import json
import csv
from sgrequests import SgRequests

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
    url = "https://branchlocator.bmoharris.com/rest/locatorsearch?like=0.2783429985749122&lang=en_US"
    payload = {
        "request": {
            "appkey": "1C92EACC-1A19-11E7-B395-EE7D55A65BB0",
            "formdata": {
                "geoip": "false",
                "dataview": "store_default",
                "limit": "1000",
                "google_autocomplete": "true",
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "55402",
                            "country": "US",
                            "latitude": 44.9754804,
                            "longitude": -93.26968599999998,
                            "state": "MN",
                            "province": "",
                            "city": "Minneapolis",
                            "address1": "",
                            "postalcode": "55402",
                        }
                    ]
                },
                "searchradius": "5000",
                "softmatch": "1",
                "where": {
                    "or": [
                        {
                            "languages": {"ilike": ""},
                            "walkupcount": {"eq": ""},
                            "driveupcount": {"eq": ""},
                            "smartbranch": {"eq": ""},
                            "grouptype": {"in": "BMOHarrisBranches"},
                            "or": {
                                "safedepositsmall": {"eq": ""},
                                "safedepositmedium": {"eq": ""},
                                "safedepositlarge": {"eq": ""},
                                "allpoint": {"eq": ""},
                                "walgreens": {"eq": ""},
                                "speedway": {"eq": ""},
                                "mobilecash": {"eq": ""},
                            },
                        },
                        {
                            "grouptype": {"eq": "BMOHarrisBranches"},
                            "lobby": {"eq": ""},
                            "secondaryid": {"eq": ""},
                        },
                    ]
                },
                "false": "0",
            },
        }
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    locs = []
    branches = []
    r = session.post(url, headers=headers, data=json.dumps(payload), verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '{"mondayopen":' in line:
            items = line.split('{"mondayopen":')
            for item in items:
                if '"collectionname":"' not in item:
                    bid = item.split(',"id":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0].lower()
                    city = (
                        item.split('"city":"')[1]
                        .split('"')[0]
                        .replace(" ", "-")
                        .lower()
                    )
                    burl = (
                        "https://branches.bmoharris.com/"
                        + state
                        + "/"
                        + city
                        + "/harris"
                        + bid
                    )
                    if bid not in locs:
                        locs.append(bid)
                        branches.append(burl)
    payload = {
        "request": {
            "appkey": "1C92EACC-1A19-11E7-B395-EE7D55A65BB0",
            "formdata": {
                "geoip": "false",
                "dataview": "store_default",
                "limit": "1000",
                "google_autocomplete": "true",
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "Kokomo IN",
                            "country": "US",
                            "latitude": 40.486427,
                            "longitude": -86.13360329999999,
                        }
                    ]
                },
                "searchradius": "5000",
                "softmatch": "1",
                "where": {
                    "or": [
                        {
                            "languages": {"ilike": ""},
                            "walkupcount": {"eq": ""},
                            "driveupcount": {"eq": ""},
                            "smartbranch": {"eq": ""},
                            "grouptype": {"in": "BMOHarrisBranches"},
                            "or": {
                                "safedepositsmall": {"eq": ""},
                                "safedepositmedium": {"eq": ""},
                                "safedepositlarge": {"eq": ""},
                                "allpoint": {"eq": ""},
                                "walgreens": {"eq": ""},
                                "speedway": {"eq": ""},
                                "mobilecash": {"eq": ""},
                            },
                        },
                        {
                            "grouptype": {"eq": "BMOHarrisBranches"},
                            "lobby": {"eq": ""},
                            "secondaryid": {"eq": ""},
                        },
                    ]
                },
                "false": "0",
            },
        }
    }
    r = session.post(url, headers=headers, data=json.dumps(payload), verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '{"mondayopen":' in line:
            items = line.split('{"mondayopen":')
            for item in items:
                if '"collectionname":"' not in item:
                    bid = item.split(',"id":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0].lower()
                    city = (
                        item.split('"city":"')[1]
                        .split('"')[0]
                        .replace(" ", "-")
                        .lower()
                    )
                    burl = (
                        "https://branches.bmoharris.com/"
                        + state
                        + "/"
                        + city
                        + "/harris"
                        + bid
                    )
                    if bid not in locs:
                        locs.append(bid)
                        branches.append(burl)

    stores = []
    for branch in branches:
        website = "bmoharris.com"
        typ = "Branch"
        hours = "<MISSING>"
        Found = False
        while Found is False:
            Found = True
            try:
                r = session.get(branch, headers=headers, timeout=10, verify=False)
                if r.encoding is None:
                    r.encoding = "utf-8"
                lines = r.iter_lines(decode_unicode=True)
                for line in lines:
                    if 'property="og:title" content="' in line:
                        name = line.split('property="og:title" content="')[1].split(
                            '"'
                        )[0]
                    if '"streetAddress":"' in line:
                        add = line.split('"streetAddress":"')[1].split('"')[0]
                    if '"addressLocality":"' in line:
                        city = line.split('"addressLocality":"')[1].split('"')[0]
                    if '"addressRegion":"' in line:
                        state = line.split('"addressRegion":"')[1].split('"')[0]
                    if '"postalCode":"' in line:
                        zc = line.split('"postalCode":"')[1].split('"')[0]
                    if '"latitude":' in line:
                        lat = line.split('"latitude":')[1].split(",")[0]
                    if '"longitude":' in line:
                        lng = (
                            line.split('"longitude":')[1]
                            .strip()
                            .replace("\r", "")
                            .replace("\n", "")
                        )
                    if '"addressCountry":"' in line:
                        country = line.split('"addressCountry":"')[1].split('"')[0]
                    if '"@id":"' in line:
                        store = (
                            line.split('"@id":"')[1].split('"')[0].replace("harris", "")
                        )
                    if '"telephone":"' in line:
                        phone = line.split('"telephone":"')[1].split('"')[0]
                    if '"dayOfWeek":[' in line:
                        g = next(lines)
                        next(lines)
                        o = next(lines)
                        c = next(lines)
                        day = g.split('"')[1]
                        ophr = o.split('":"')[1].split('"')[0]
                        clhr = c.split('":"')[1].split('"')[0]
                        if hours == "<MISSING>":
                            hours = day + ": " + ophr + "-" + clhr
                        else:
                            hours = hours + "; " + day + ": " + ophr + "-" + clhr
                    if "</html>" in line:
                        if store not in stores:
                            stores.append(store)
                            hours = hours.replace("closed-closed", "closed")
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
            except:
                Found = False


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
