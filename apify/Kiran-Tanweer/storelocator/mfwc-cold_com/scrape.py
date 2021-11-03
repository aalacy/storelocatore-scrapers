from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("mfwc-cold_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    search_url = "https://www.mfwc-cold.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    script = soup.findAll("script", {"type": "application/ld+json"})[1]
    script = str(script)
    script = script.replace("</script>", "")
    script = script.replace('<script type="application/ld+json">', "")
    script = script.strip()
    script = json.loads(script)
    for loc in script["@graph"]:
        title = loc["name"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        phone = loc["address"]["telephone"]
        if "geo" in loc:
            lat = loc["geo"]["latitude"]
            lng = loc["geo"]["longitude"]
        else:
            lat = "<MISSING>"
            lng = "<MISSING>"
        phone = str(phone)
        phone = phone.split("',")[0].lstrip("['")

        data.append(
            [
                "https://www.mfwc-cold.com/",
                search_url,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                lng,
                "<MISSING>",
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
