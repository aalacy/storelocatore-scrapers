import csv
import re
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def find_locs():
    url = "https://www.pizzaking.com/locations/"
    citybaseurl = "https://www.pizzaking.com/location-category/"
    linklist = []
    citylist = []
    r = session.get(url, headers=headers)
    loclist = r.text.split('<section class="entry-content cf">', 1)[1].split(
        "</section>", 1
    )[0]
    loclist = loclist.split("<h3>")[1:]

    for loc in loclist:
        citylist.append(loc.split("</h3>")[0])
    while "" in citylist:
        citylist.remove("")

    for city in citylist:
        city = city.replace(" ", "-")
        city = city.replace(u"\xa0", u"")
        cityurl = citybaseurl + city
        try:
            r = session.get(cityurl, headers=headers)
            r = r.text.split('<h1 class="h2 entry-title">')
            locs = []
            for r in r:
                r = r.split("</h1>", 1)[0]
                locs.append(r)
            locs = locs[1:]
            for loc in locs:
                link = re.findall('".+?"', loc)[0][1:-1]
                linklist.append(link)
        except:
            pass

    x = 1
    y = 0
    while x != y:
        x = len(linklist)
        newlinklist = []
        for link in linklist:
            try:
                rplink = link + "?relatedposts=1"
                r = session.get(rplink, headers=headers)
                r = r.text.replace("\\/", "/").split("url")
                r = [r[1][3:-3], r[3][3:-3], r[5][3:-3]]
                newlinklist.append(link)
                for newlink in r:
                    newlinklist.append(newlink)
            except:
                newlinklist.append(link)
        [linklist.append(x) for x in newlinklist if x not in linklist]
        y = len(linklist)
    return linklist


def fetch_data(linklist):
    data = []
    url = "https://www.pizzaking.com/"
    for link in linklist:
        loctype = "<MISSING>"
        loc_data = []
        r = session.get(link, headers=headers)
        lat = r.text.split(',"lat":"')[1].split('",')[0]
        lng = r.text.split(',"lng":"')[1].split('",')[0]
        name = r.text.split('{"store":"')[1].split('",')[0]
        name = name.replace("&#8211;", "-")
        name = name.replace("&#8217;", "'")
        name = name.replace("\/", "/")
        if "(Franchise)" in name:
            name = name.replace("(Franchise)", "")
            loctype = "Franchise"
        street = r.text.split(',"address":"')[1].split('",')[0]
        if street == "Online Ordering Available":
            street = r.text.split(',"address2":"')[1].split('",')[0]
        city = r.text.split(',"city":"')[1].split('",')[0]
        state = r.text.split(',"state":"')[1].split('",')[0]
        zipcode = r.text.split(',"zip":"')[1].split('",')[0]
        country = r.text.split(',"country":"')[1].split('",')[0]
        contact = r.text.split('<div class="wpsl-contact-details">', 1)[1].split(
            "</div>", 1
        )[0]
        phone = contact.split("<span>", 1)[1].split("</span>", 1)[0]
        time = r.text.split(
            '<table role="presentation" class="wpsl-opening-hours">', 1
        )[1].split("</table>", 1)[0]
        time = time.split("<tr>")[1:]
        hoo = ""
        for day in time:
            dayname = day.split("<td>", 1)[1].split("</td>", 1)[0]
            try:
                hours = day.split("<time>", 1)[1].split("</time>", 1)[0]
            except:
                hours = day.split("<td>")[2].split("</td>", 1)[0]
            hoo = hoo + dayname + " " + hours + ", "
        hoo = hoo[0:-2]
        loc_data.append(url)
        loc_data.append(link)
        loc_data.append(name)
        loc_data.append(street)
        loc_data.append(city)
        loc_data.append(state)
        loc_data.append(zipcode)
        loc_data.append(country)
        loc_data.append("<MISSING>")
        loc_data.append(phone)
        loc_data.append(loctype)
        loc_data.append(lat)
        loc_data.append(lng)
        loc_data.append(hoo)
        loc_data = ["<MISSING>" if point is None else point for point in loc_data]
        loc_data = ["<MISSING>" if point is "" else point for point in loc_data]
        data.append(loc_data)
    return data


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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


def scrape():
    linklist = find_locs()
    data = fetch_data(linklist)
    write_output(data)


scrape()
