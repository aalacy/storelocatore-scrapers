import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("baskinrobbins_co_uk")


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
    ids = []
    cities = [
        "London",
        "Birmingham",
        "Glasgow",
        "Liverpool",
        "Bristol",
        "Manchester",
        "Sheffield",
        "Leeds",
        "Edinburgh",
        "Leicester",
        "Coventry",
        "Bradford",
        "Cardiff",
        "Belfast",
        "Nottingham",
        "Kingston%20upon%20Hull",
        "Newcastle%20upon%20Tyne",
        "Stoke%20on%20Trent",
        "Southampton",
        "Derby",
        "Portsmouth",
        "Brighton%20and%20Hove",
        "Plymouth",
        "Northampton",
        "Reading",
        "Luton",
        "Wolverhampton",
        "Bournemouth",
        "Aberdeen",
        "Bolton",
        "Norwich",
        "Swindon",
        "Swansea",
        "Milton%20Keynes",
        "Southend%20on%20Sea",
        "Middlesbrough",
        "Sunderland",
        "Peterborough",
        "Warrington",
        "Oxford",
        "Huddersfield",
        "Slough",
        "York",
        "Poole",
        "Cambridge",
        "Dundee",
        "Ipswich",
        "Telford",
        "Gloucester",
        "Blackpool",
        "Birkenhead",
        "Watford",
        "Sale",
        "Colchester",
        "Newport",
        "Solihull",
        "High%20Wycombe",
        "Exeter",
        "Gateshead",
        "Cheltenham",
        "Blackburn",
        "Maidstone",
        "Chelmsford",
        "Basildon",
        "Salford",
        "Basingstoke",
        "Worthing",
        "Eastbourne",
        "Doncaster",
        "Crawley",
        "Rotherham",
        "Rochdale",
        "Stockport",
        "Gillingham",
        "Sutton%20Coldfield",
        "Woking",
        "Wigan",
        "Lincoln",
        "St%20Helens",
        "Oldham",
        "Worcester",
        "Wakefield",
        "Hemel%20Hempstead",
        "Bath",
        "Preston",
        "Rayleigh",
        "Barnsley",
        "Stevenage",
        "Southport",
        "Hastings",
        "Bedford",
        "Darlington",
        "Halifax",
        "Hartlepool",
        "Chesterfield",
        "Grimsby",
        "Nuneaton",
        "Weston%20super%20Mare",
        "Chester",
        "St%20Albans",
    ]
    for cname in cities:
        url = (
            "http://baskinrobbins.co.uk/store_locator/ajaxHandler.aspx?txtPostcode="
            + cname
            + "&a=0.3488504626519726&npostcode="
            + cname
        )
        r = session.get(url, headers=headers)
        website = "baskinrobbins.co.uk"
        typ = "<MISSING>"
        country = "GB"
        loc = "<MISSING>"
        store = "<MISSING>"
        hours = "<MISSING>"
        logger.info("Pulling Stores")
        g = (
            str(r.content.decode("utf-8"))
            .replace("\r", "")
            .replace("\t", "")
            .replace("\n", "")
        )
        if "</strong><strong>" in g:
            items = g.split("</strong><strong>")
            for item in items:
                if "</strong><br /><br />" not in item:
                    try:
                        phone = item.split(">Tel:")[1].split("<")[0].strip()
                    except:
                        phone = "<MISSING>"
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    state = "<MISSING>"
                    name = item.split("<")[0].strip()
                    address = (
                        item.split("</strong><br />")[1].split("<br />Tel:")[0].strip()
                    )
                    if address.count("<br />") == 3:
                        add = (
                            address.split("<br />")[0]
                            + " "
                            + address.split("<br />")[1]
                        )
                        city = address.split("<br />")[2]
                        zc = address.split("<br />")[3]
                    if address.count("<br />") == 2:
                        add = address.split("<br />")[0]
                        city = address.split("<br />")[1]
                        zc = address.split("<br />")[2]
                    if address.count("<br />") == 1:
                        add = address.split("<br />")[0]
                        city = "<MISSING>"
                        zc = address.split("<br />")[1]
                    add = add.strip()
                    addinfo = add + "|" + city + "|" + zc
                    phone = phone.replace("-", "").strip()
                    if phone == "":
                        phone = "<MISSING>"
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
