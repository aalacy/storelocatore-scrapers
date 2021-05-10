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
    linesone = r.iter_lines()
    for line in linesone:
        line = str(line.decode("utf-8"))
        if (
            '<h2 class="elementor-heading-title elementor-size-default"><a href="'
            in line
        ):
            lurl = line.split(
                '<h2 class="elementor-heading-title elementor-size-default"><a href="'
            )[1].split('"')[0]
        if '<div class="elementor-text-editor elementor-clearfix">' in line:
            g = next(linesone)
            g = str(g.decode("utf-8"))
            try:
                a5 = g.split('">(')[1].split("<")[0]
            except:
                pass
            try:
                a5 = g.split(';">(')[1].split("<")[0]
            except:
                pass
            if (
                '</p><p><span style="font-size: 15px;">' not in g
                and '</p><p class="p1"><span style="font-size: 15px;">' not in g
            ):
                a1 = g.split(">")[1].split("<")[0].replace(",", "")
                a2 = g.split("</p><p>")[1].split(",")[0]
                a3 = g.split("</p><p>")[1].split("<")[0].split(",")[1].strip()
                a4 = g.split("</p><p>")[1].split("<")[0].strip().rsplit(" ", 1)[1]
                try:
                    a5 = g.split("</p><p>")[2].split("<")[0].strip()
                except:
                    a5 = "<MISSING>"
            else:
                a1 = g.split(">")[1].split("<")[0].replace(",", "")
                try:
                    a2 = g.split('</p><p><span style="font-size: 15px;">')[1].split(
                        ","
                    )[0]
                except:
                    a2 = g.split('</p><p class="p1"><span style="font-size: 15px;">')[
                        1
                    ].split(",")[0]
                a3 = g.split('</span><span style="font-size: 15px;">')[1].split(",")[0]
                a4 = (
                    g.split('</span><span style="font-size: 15px;">')[2]
                    .split("<")[0]
                    .strip()
                )
            locs.append(lurl + "|" + a1 + "|" + a2 + "|" + a3 + "|" + a4 + "|" + a5)
    for loc in locs:
        store = "<MISSING>"
        name = ""
        add = loc.split("|")[1]
        city = loc.split("|")[2]
        state = loc.split("|")[3]
        zc = loc.split("|")[4]
        purl = loc.split("|")[0]
        phone = loc.split("|")[5]
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        typ = "<MISSING>"
        r2 = session.get(purl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("&")[0].strip()
                if "|" in name:
                    name = name.split("|")[0].strip()
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
