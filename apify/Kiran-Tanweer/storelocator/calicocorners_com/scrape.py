from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("calicocorners_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        temp_list = []  # ignoring duplicates
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
    url = "https://www.calicocorners.com/storelocator.aspx"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    script = soup.findAll("script")[13]
    script = str(script)
    script = script.split("var locations=[")[1]
    locations = script.split("</div>'],")
    for loc in locations:
        coords = loc.split('<div class="storehours')[0]
        coords = coords.split(",")
        title = coords[0].strip()
        title = title.replace("'", "")
        title = title.lstrip("[")
        lat = coords[1].strip()
        lng = coords[2].strip()
        address = (
            loc.split('<div class="storehours pad-no" style="width:100%;"><br/>')[1]
            .split("<br/>Phone:")[0]
            .strip()
        )
        phone = loc.split("Phone: ")[1].split("<br/>Email:")[0].strip()
        hours = loc.split(
            '<div class="storehours storehr-popup" style="width:100%;padding-top:5px;">'
        )[1].split('</div><br/><div class="calicoalinkdiv">')[0]
        link = loc.split('"trackOutboundLink(&#39;')[1].split(" &#39")[0]
        address = address.replace("<br/>", ",")
        address = address.replace("     ", ",")
        address = address.lstrip("Driscoll Place Shopping Center,")
        address = address.lstrip("Rue De France,")
        address = address.lstrip("Seneca Square,")
        address = address.lstrip("Kingspointe Village Shopping Center,")
        address = address.lstrip("dgewood Gateway Center,")
        address = address.lstrip("Merchant&#39;s Walk Shopping Center,")
        address = address.split(",")
        pcode = address[-1].strip()
        state = address[-2].strip()
        city = address[-3].strip()
        if len(address) == 5:
            street = address[0].strip() + " " + address[1].strip()
        else:
            street = address[0].strip()
        hours = hours.replace("<br/>", ", ")
        store_url = "https://www.calicocorners.com/" + link
        storeid = link.split("=")[1].STRIP()

        data.append(
            [
                "https://www.calicocorners.com/",
                store_url,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
                phone,
                "<MISSING>",
                lat,
                lng,
                hours,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
