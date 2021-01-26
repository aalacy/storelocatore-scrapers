import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("timberland_com")


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
    url = "https://hosted.where2getit.com/timberland/local/ajax?lang=en-EN&xml_request=%3Crequest%3E%3Cappkey%3E3BD8F794-CA9E-11E5-A9D5-072FD1784D66%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Corder%3Eretail_store%2Cfactory_outlet%2Crank+ASC%2C_distance%3C%2Forder%3E%3Climit%3E2500%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E10002%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3Ccountry%3E%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Cradiusuom%3E%3C%2Fradiusuom%3E%3Csearchradius%3E5000%3C%2Fsearchradius%3E%3Cwhere%3E%3Cor%3E%3Cretail_store%3E%3Ceq%3E1%3C%2Feq%3E%3C%2Fretail_store%3E%3Cfactory_outlet%3E%3Ceq%3E1%3C%2Feq%3E%3C%2Ffactory_outlet%3E%3Cauthorized_reseller%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fauthorized_reseller%3E%3Cicon%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ficon%3E%3Cpro_workwear%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpro_workwear%3E%3Cpro_footwear%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpro_footwear%3E%3Ctree_footwear%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftree_footwear%3E%3Ctree_apparel%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftree_apparel%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    r = session.get(url, headers=headers)
    website = "timberland.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<name>" in line:
            name = (
                line.split("<name>")[1].split("<")[0].replace("&amp;reg&lt;br&gt;", "")
            )
            name = name.replace("&lt;br&gt;", "")
            name = name.replace("&amp;reg", "")
            hours = ""
        if "<address1>" in line:
            add = line.split("<address1>")[1].split("<")[0]
        if "<address2>" in line:
            add = add + " " + line.split("<address2>")[1].split("<")[0]
            add = add.strip()
        if "<city>" in line:
            city = line.split("<city>")[1].split("<")[0]
        if "<state>" in line:
            state = line.split("<state>")[1].split("<")[0]
        if "<lat>" in line:
            lat = line.split("<latitude>")[1].split("<")[0]
        if "<lng>" in line:
            lng = line.split("<longitude>")[1].split("<")[0]
        if "<phone>" in line:
            phone = line.split("<phone>")[1].split("<")[0]
        if "<clientkey>" in line:
            store = line.split("<clientkey>")[1].split("<")[0]
        if "<postalcode>" in line:
            zc = line.split("<postalcode>")[1].split("<")[0]
        if "<su>" in line:
            hours1 = "Sun: " + line.split("<su>")[1].split("<")[0]
        if "<m>" in line:
            hours2 = "Mon: " + line.split("<m>")[1].split("<")[0]
        if "<t>" in line:
            hours3 = "Tue: " + line.split("<t>")[1].split("<")[0]
        if "<w>" in line:
            hours4 = "Wed: " + line.split("<w>")[1].split("<")[0]
        if "<thu>" in line:
            hours5 = "Thu: " + line.split("<thu>")[1].split("<")[0]
        if "<f>" in line:
            hours6 = "Fri: " + line.split("<f>")[1].split("<")[0]
        if "<sa>" in line:
            hours7 = "Sat: " + line.split("<sa>")[1].split("<")[0]
        if "</poi>" in line:
            hours = (
                hours1
                + "; "
                + hours2
                + "; "
                + hours3
                + "; "
                + hours4
                + "; "
                + hours5
                + "; "
                + hours6
                + "; "
                + hours7
            )
            if state != "":
                if (
                    "am" not in hours
                    and "pm" not in hours
                    and "closed" not in hours.lower()
                ):
                    hours = "<MISSING>"
                name = name.replace("Timberland", "Timberland ").replace("  ", " ")
                loc = (
                    "https://locations.timberland.com/"
                    + state.lower()
                    + "/"
                    + city.lower().replace(" ", "-")
                    + "/"
                    + store
                    + "/"
                )
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
