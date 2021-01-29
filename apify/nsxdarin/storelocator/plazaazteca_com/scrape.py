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
    url = "https://plazaazteca.com/locations/"
    r = session.get(url, headers=headers)
    website = "plazaazteca.com"
    country = "US"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            '<h2 class="elementor-heading-title elementor-size-default"><a href="'
            in line
        ):
            lurl = line.split(
                '<h2 class="elementor-heading-title elementor-size-default"><a href="'
            )[1].split('"')[0]
            if lurl not in locs:
                locs.append(lurl)
    for loc in locs:
        store = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        typ = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("&")[0].strip()
                if "|" in name:
                    name = name.split("|")[0].strip()
            if (
                '<div class="elementor-text-editor elementor-clearfix lazyload"><p'
                in line2
                and "At Plaza" not in line2
                and "We invite" not in line2
                and "Welcome to the" not in line2
            ):
                if "2835 Lehigh St" in line2:
                    add = "2835 Lehigh St"
                    city = "Allentown"
                    state = "Pennsylvania"
                    zc = "18103"
                    phone = "(484) 656 7277"
                elif "153 S Gulph Rd" in line2:
                    add = "153 S Gulph Rd"
                    city = "King of Prussia"
                    state = "Pennsylvania"
                    zc = "19406"
                    phone = "(610) 265-1170"
                elif "821 W Lancaster Ave" in line2:
                    add = "821 W Lancaster Ave"
                    city = "Wayne"
                    state = "Pennsylvania"
                    zc = "19087"
                    phone = "484-580-6369"
                elif "6623 W Broad St" in line2:
                    add = "6623 W Broad St"
                    city = "Richmond"
                    state = "Virginia"
                    zc = "23230"
                    phone = "804-888-9984"
                elif "/suffolk" in loc:
                    add = "1467 N Main St"
                    city = "Suffolk"
                    state = "Virginia"
                    zc = "23434"
                    phone = "(757) 925-1222"
                elif "/warwick" in loc:
                    add = "12428 Warwick Blvd"
                    city = "Newport News"
                    state = "Virginia"
                    zc = "23606"
                    phone = "(757) 599-6727"
                elif "/greenville" in loc:
                    add = "400 Greenville Blvd SW"
                    city = "Greenville"
                    state = "North Carolina"
                    zc = "27834"
                    phone = "(252) 321-8008"
                elif "/newington" in loc:
                    add = "3260 Berlin Tpke"
                    city = "Newington"
                    state = "Connecticut"
                    zc = "06111"
                    phone = "(860) 436-9708"
                else:
                    add = line2.split(
                        '<div class="elementor-text-editor elementor-clearfix lazyload"><p'
                    )[1].split(",")[0]
                    city = line2.split("</p><p")[1].split(">")[1].split(",")[0]
                    state = line2.split("</p><p")[1].split(">")[1].split(",")[1].strip()
                    zc = line2.split("</p><p")[1].split(">")[1].split(",")[2].strip()
                    phone = line2.split("</p><p")[2].split(">")[1].split("<")[0]
            if (
                '<div class="elementor-text-editor elementor-clearfix lazyload"><p class="p1">'
                in line2
            ):
                add = line2.split(
                    '<div class="elementor-text-editor elementor-clearfix lazyload"><p class="p1">'
                )[1].split("<")[0]
                city = line2.split('Sans-serif;">')[1].split(",")[0]
                state = line2.split('Sans-serif;">')[2].split(",")[0]
                zc = line2.split('Sans-serif;">')[3].split("<")[0]
            if "<span >" in line2 and "<span ><" not in line2 and "</span>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "<p" not in g:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                if 'font-weight: 500;">' in g:
                    hinfo = g.split('font-weight: 500;">')[1].split("<")[0]
                else:
                    hinfo = g.split('">')[1].split("<")[0]
                hrs = line2.split("<span >")[1].split("<")[0] + ": " + hinfo
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '<p class="p1">(' in line2:
                phone = line2.split('<p class="p1">(')[1].split("<")[0]
            if "</p" in add:
                add = add.split("<")[0]
            if "1467 N Main St" in add:
                city = "Suffolk"
                state = "Virginia"
                zc = "23434"
                phone = "(757) 925-1222"
            if "12428 Warwick Blvd" in add:
                city = "Newport News"
                state = "Virginia"
                zc = "23606"
                phone = "(757) 599-6727"
            if "greenville" in loc:
                add = "400 Greenville Blvd SW"
                city = "Greenville"
                state = "North Carolina"
                zc = "27834"
                phone = "(252) 321-8008"
            if "newington" in loc:
                add = "3260 Berlin Tpke"
                city = "Newington"
                state = "Connecticut"
                zc = "06111"
                phone = "860-436-9708"
            if "www.toroazteca.com" in loc:
                add = "194 Buckland Hills Drive Suite 1052"
                city = "Manchester"
                state = "Connecticut"
                zc = "06042"
                phone = "860-648-4454"
                hours = "Monday - Thursday: 11am - 10pm (Bar Open Late); Friday - Saturday: 11am - 11pm (Bar Open Late); Sunday: 11:30am - 10pm (Bar Open Late)"
            if "<" in name:
                name = name.split("<")[0]
        if "Coming Soon" not in name:
            if ">" in add:
                add = add.split(">")[1].strip()
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
