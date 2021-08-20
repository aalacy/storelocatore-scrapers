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
    url = "https://www.dollarstore.ca/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug/"
    r = session.get(url, headers=headers)
    website = "dollarstore.ca"
    typ = "<MISSING>"
    country = "CA"
    loc = "<MISSING>"
    hours = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"map_id":"' in line:
            items = line.split('"map_id":"')
            for item in items:
                if '"address":"' in item:
                    name = item.split('"title":"')[1].split('"')[0]
                    addinfo = item.split('"address":"')[1].split('"')[0]
                    phone = item.split('"description":"')[1].split('"')[0]
                    store = name.split("#")[1].strip()
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    if "24018 Woodbine Avenue" in addinfo:
                        add = "Unit A-01, 24018 Woodbine Avenue"
                        city = "Keswick"
                        state = "ON"
                        zc = "L4P 3E9"
                    else:
                        if addinfo.count(",") == 2:
                            add = addinfo.split(",")[0].strip()
                            city = addinfo.split(",")[1].strip()
                            state = addinfo.split(",")[2].strip().split(" ")[0]
                            zc = addinfo.strip().rsplit(" ", 1)[1].strip()
                        elif addinfo.count(",") == 3:
                            add = addinfo.split(",")[0].strip()
                            city = addinfo.split(",")[1].strip()
                            state = addinfo.split(",")[2].strip()
                            zc = addinfo.split(",")[3].strip()
                        elif addinfo.count(",") == 4:
                            add = (
                                addinfo.split(",")[0].strip()
                                + " "
                                + addinfo.split(",")[1].strip()
                            )
                            city = addinfo.split(",")[2].strip()
                            state = addinfo.split(",")[3].strip()
                            zc = addinfo.split(",")[4].strip()
                        else:
                            add = (
                                addinfo.split(",")[1].strip()
                                + " "
                                + addinfo.split(",")[1].strip()
                                + " "
                                + addinfo.split(",")[2]
                            )
                            city = addinfo.split(",")[3].strip()
                            state = addinfo.split(",")[4].strip()
                            zc = addinfo.split(",")[5].strip()
                    if city == "Kamloops":
                        state = "BC"
                    if city == "Garson":
                        state = "ON"
                    if "Can" in zc:
                        zc = "<MISSING>"
                    if ">" in phone:
                        phone = phone.split(">")[1].split("<")[0]
                    if phone == "":
                        phone = "<MISSING>"
                    if "0000" in lat or "0000" in lng:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
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
