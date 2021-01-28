import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("texashealth_org")


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
    locs = []
    locinfo = []
    url = "https://www.texashealth.org//sxa/search/results/?s={E6D4398E-5377-4F52-A622-BA5985AA0E05}|{489713F2-2F53-486A-A99A-125A4921BB4F}&itemid={AF045BC3-3192-47D4-9F02-14F252C53DC8}&sig=location-search&g=32.735687%7C-97.10806559999997&o=DistanceMi%2CAscending&p=2000&e=0&v=%7B46E173AB-F518-41E7-BFB5-00206EDBA9E6%7D"
    r = session.get(url, headers=headers)
    website = "texashealth.org"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"Url":"' in line:
            items = line.split('"Url":"')
            for item in items:
                if '"Name":' in item:
                    try:
                        ltyp = (
                            item.split('"PoiIcon":"')[1]
                            .split('.png"')[0]
                            .rsplit("_", 1)[1]
                        )
                    except:
                        ltyp = "<MISSING>"
                    lurl = "https://texashealth.org" + item.split('"')[0]
                    lurl = lurl.replace("https://texashealth.orghttps", "https")
                    locs.append(lurl + "|" + ltyp)
    for loc in locs:
        name = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        store = "<MISSING>"
        typ = loc.split("|")[1]
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        phone = ""
        locinfo = []
        ll = []
        logger.info(loc.split("|")[0])
        r2 = session.get(loc.split("|")[0], headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
                if "|" in name:
                    name = name.split("|")[0].strip()
            if '<div class="row profile-details">' in line2:
                items = line2.split('<div class="row profile-details">')
                for item in items:
                    if '<div class="field-address-line-1">' in item:
                        name = item.split('"profile-key-data field-title">')[1].split(
                            "<"
                        )[0]
                        add = item.split('<div class="field-address-line-1">')[1].split(
                            "<"
                        )[0]
                        try:
                            add = (
                                add
                                + " "
                                + line2.split('<div class="field-address-line-2">')[
                                    1
                                ].split("<")[0]
                            )
                            add = add.strip()
                        except:
                            pass
                        city = item.split('<span class="field-city">')[1].split("<")[0]
                        state = item.split('<span class="field-state">')[1].split("<")[
                            0
                        ]
                        zc = item.split('<span class="field-zip-code">')[1].split("<")[
                            0
                        ]
                        phone = item.split('"field-phone-number" href="tel:')[1].split(
                            '"'
                        )[0]
                        locinfo.append(
                            name
                            + "|"
                            + add
                            + "|"
                            + city
                            + "|"
                            + state
                            + "|"
                            + zc
                            + "|"
                            + phone
                        )
            if "Image&quot;:&quot;&quot;,&quot;Latitude&quot;:&quot;" in line2:
                items = line2.split(
                    "Image&quot;:&quot;&quot;,&quot;Latitude&quot;:&quot;"
                )
                for item in items:
                    if "&quot;Address&quot;:&" in item:
                        llat = item.split("&")[0]
                        llng = item.split("&quot;Longitude&quot;:&quot;")[1].split("&")[
                            0
                        ]
                        ll.append(llat + "|" + llng)
        for x in range(0, len(locinfo)):
            name = locinfo[x].split("|")[0]
            add = locinfo[x].split("|")[1]
            city = locinfo[x].split("|")[2]
            state = locinfo[x].split("|")[3]
            zc = locinfo[x].split("|")[4]
            phone = locinfo[x].split("|")[5]
            lat = ll[x].split("|")[0]
            lng = ll[x].split("|")[1]
            if phone == "":
                phone = "<MISSING>"
            info = name + "|" + add + "|" + phone
            if info not in locinfo:
                locinfo.append(info)
                yield [
                    website,
                    loc.split("|")[0],
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
