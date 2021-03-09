import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
}

logger = SgLogSetup().get_logger("historicengland_org_uk__listing__the-list")


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
                "raw_address",
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
    regions = [
        "EAST MIDLANDS",
        "EAST OF ENGLAND",
        "LONDON",
        "LONDON AND SOUTH EAST",
        "MIDLANDS",
        "NORTH EAST",
        "NORTH EAST AND YORKSHIRE",
        "NORTH WEST",
        "SOUTH EAST",
        "SOUTH WEST",
        "WEST MIDLANDS",
        "YORKSHIRE",
        "YORKSHIRE AND THE HUMBER",
    ]

    website = "historicengland.org.uk/listing/the-list"
    typ = "Park & Garden"
    country = "GB"
    for region in regions:
        logger.info(region)
        for x in range(1, 5):
            logger.info(str(x))
            url = (
                "https://historicengland.org.uk/listing/the-list/advanced-search-results?ListEntryNumber=&AssetName=&County=&District=&Parish=&MainQuery=&ListEntryText=&Grade=&HCListedBuilding=false&HCScheduledMonument=false&HCWreck=false&HCParkAndGarden=4&HCParkAndGarden=false&HCBattlefield=false&HCWorldHeritageSite=false&HCCertificateOfImmunity=false&HCBuildingPreservationNotice=false&ThesaurusTerm=&Period=&FromDate=&FromDateADBC=AD&ToDate=&ToDateADBC=AD&DesignationFromDateInput=&DesignationToDateInput=&OldRecordNumber=&Person=&ParliamentaryConstituency=&GovernmentRegion="
                + region.replace(" ", "+")
                + "&btnSubmit=&searchResultsPerPage=100&page="
                + str(x)
            )
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                line = str(line.decode("utf-8"))
                if '<a href="/listing/the-list/list-entry/' in line:
                    lurl = (
                        "https://historicengland.org.uk"
                        + line.split('href="')[1].split('"')[0]
                    )
                    if lurl not in locs:
                        locs.append(lurl)
        for loc in locs:
            logger.info(loc)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = "<MISSING>"
            phone = "<MISSING>"
            rawadd = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = "<MISSING>"
            r2 = session.get(loc, headers=headers)
            lines = r2.iter_lines()
            for line2 in lines:
                line2 = str(line2.decode("utf-8"))
                if '<h1 class="h1">' in line2:
                    name = line2.split('<h1 class="h1">')[1].split("<")[0]
                if "Statutory Address:</dt>" in line2:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                    rawadd = g.split("<dd>")[1].split("<")[0].strip()
                    addr = parse_address_intl(rawadd)
                    city = addr.city
                    zc = addr.postcode
                    add = addr.street_address_1
                if "County:</dt>" in line2:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                    state = g.split(">")[1].split("<")[0]
                    if state == "":
                        state = "<MISSING>"
            if zc == "" or zc is None:
                zc = "<MISSING>"
            if city == "" or city is None:
                city = "<MISSING>"
            if add == "" or add is None:
                add = "<MISSING>"
            if rawadd == "":
                rawaddd = "<MISSING>"
            if state == "" or state is None:
                state = "<MISSING>"
            yield [
                website,
                loc,
                name,
                rawadd,
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
