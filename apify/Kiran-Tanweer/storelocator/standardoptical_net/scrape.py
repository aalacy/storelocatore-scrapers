from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("standardoptical_net")

session = SgRequests()

headers = {
    "authority": "www.standardoptical.net",
    "method": "GET",
    "path": "/locations/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "_ga=GA1.2.733661259.1614820489; _fbp=fb.1.1614820490075.647603882; _hjTLDTest=1; _hjid=8e6475d7-3e32-4a1b-bbbb-10463f5ecd5f; calltrk_referrer=direct; calltrk_landing=https%3A//www.standardoptical.net/locations/; calltrk_session_id=9423bd09-dec9-466e-87d3-9280bafd5982; __zlcmid=12wjqyswsyHU0KI; _gid=GA1.2.1382793327.1615076356; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=1; _hjIncludedInSessionSample=0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
}

headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    url = "https://www.standardoptical.net/locations/"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loc = soup.find(
        "div",
        {"class": "et_pb_section et_pb_section_3 location-list et_section_regular"},
    )
    rows = loc.findAll("div", {"class": "et_pb_row"})
    for row in rows:
        locs = row.findAll("div", {"class": "et_pb_column"})
        for loc in locs:
            container = loc.find("div", {"class": "container"})
            if container is not None:
                link = container.find("a")["href"]
                if link.find("standardoptical") == -1:
                    link = "https://www.standardoptical.net/" + link
                title = loc.find("h2", {"class": "loc_heading_two"}).text
                address = str(loc.find("p", {"class": "loc_add"}))
                address = address.replace("\n", " ")
                phone = loc.find("a", {"class": "tel_btn"}).text.strip()
                r = session.get(link, headers=headers2)
                bs = BeautifulSoup(r.text, "html.parser")
                bs = str(bs)
                try:
                    hours = bs.split(
                        '<p style="text-align: center;"><span style="font-size: medium; color:'
                    )[1].split("</p>")[0]
                except IndexError:
                    hours = bs.split(
                        '<p style="text-align: center;"><span style="font-size: large; color:'
                    )[1].split("</p>")[0]
                hours = hours.replace(
                    '</span><br/><span style="font-size: medium; color: #ffffff;">', " "
                )
                hours = hours.rstrip("</span>")
                hours = hours.lstrip(' #ffffff;">')
                hours = hours.replace(
                    '</span><br/><span style="font-size: medium; color: #fff;">', " "
                )
                hours = hours.replace(
                    '</span><br/> <span style="font-size: medium; color: #ffffff;">',
                    " ",
                )
                hours = hours.replace("\n", " ")
                hours = hours.replace(
                    '</span><br/> <span style="font-size: medium; color: #ffffff;">',
                    " ",
                )
                hours = hours.replace(
                    '</span><br/> <span style="font-size: medium; color: #fff;">', " "
                )
                hours = hours.replace(
                    '</span><br/> <span style="font-size: large; color: #ffffff;">', " "
                )
                hours = hours.replace("<br/>", "")
                hours = hours.replace("<span>", "")
                hours = hours.replace("</span></span>", "")
                hours = hours.replace("  ", " ")

                address = address.lstrip('<p class="loc_add">')
                address = address.rstrip("</p>")
                address = address.split("<br/>")
                street = address[0]
                locality = address[1]
                locality = locality.split(",")
                city = locality[0].strip()
                statecode = locality[1].strip()
                statecode = statecode.split(" ")
                state = statecode[0].strip()
                pcode = statecode[1].strip()

                req = session.get(link, headers=headers2)
                bs = BeautifulSoup(req.text, "html.parser")

                coords = bs.findAll("a")
                center = []
                for c in coords:
                    if c["href"].find("google.com/maps") != -1:
                        coords = c["href"]
                        center.append(coords)
                    else:
                        coords = "<MISSING>"
                if center:
                    coords = center[0]
                    lat, lng = coords.split("/@")[1].split(",1")[0].split(",")
                else:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                data.append(
                    [
                        "https://www.standardoptical.net/",
                        link,
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
