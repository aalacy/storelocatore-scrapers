import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("accessstorage_ca")


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
    url = "https://www.accessstorage.ca/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "accessstorage.ca"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<loc>https://www.accessstorage.ca/en/self-storage/' in line:
            items = line.split('<loc>https://www.accessstorage.ca/en/self-storage/')
            for item in items:
                if '<!DOCTYPE' not in item:
                    lurl = 'https://www.accessstorage.ca/en/self-storage/' + item.split('<')[0]
                    if lurl.count('/') == 7 and '/business/' not in lurl:
                        locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<h1 class="locationName">' in line2:
                name = line2.split('<h1 class="locationName">')[1].split('<')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"@type": "OpeningHoursSpecification"' in line2 and hours == '':
                days = line2.split('"@type": "OpeningHoursSpecification"')
                for day in days:
                    if '"opens"' in day:
                        hrs = day.split('http://schema.org/')[1].split('"')[0] + ': ' + day.split('"opens": "')[1].split('"')[0] + '-' + day.split('"closes": "')[1].split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
            if '"latitude": ' in line2:
                lat = line2.split('"latitude": ')[1].split(',')[0]
            if '"longitude": ' in line2:
                lng = line2.split('"longitude": ')[1].strip().replace('\r','').replace('\n','').replace('\t','')
        if add != '':
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
