import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time

logger = SgLogSetup().get_logger("selectmedical_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
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
    session = SgRequests()
    url = "https://www.selectmedical.com//sxa/search/results/?s={648F4C3A-C9EA-4FCF-82A3-39ED2AC90A06}&itemid={94793D6A-7CC7-4A8E-AF41-2FB3EC154E1C}&sig=&autoFireSearch=true&v={D2D3D65E-3A18-43DD-890F-1328E992446A}&p=50&e=0&g=&o=Distance,Ascending"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    count = 0
    for line in r.iter_lines(decode_unicode=True):
        if '"Count":' in line:
            count = int(line.split('"Count":')[1].split(",")[0])
    logger.info(("Found %s Locations..." % str(count)))
    for x in range(0, count + 9, 8):
        logger.info(("Pulling Results %s..." % str(x)))
        url2 = (
            "https://www.selectmedical.com//sxa/search/results/?s={648F4C3A-C9EA-4FCF-82A3-39ED2AC90A06}&itemid={94793D6A-7CC7-4A8E-AF41-2FB3EC154E1C}&sig=&autoFireSearch=true&v=%7BD2D3D65E-3A18-43DD-890F-1328E992446A%7D&p=8&g=&o=&e="
            + str(x)
        )
        session = SgRequests()
        time.sleep(7)
        r2 = session.get(url2, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"Id":"' in line2:
                items = line2.split('"Id":"')
                for item in items:
                    if '"Language":"e' in item:
                        website = "selectmedical.com"
                        try:
                            name = (
                                item.split('data-variantfieldname=\\"Link')[1]
                                .split(">")[1]
                                .split("<")[0]
                            )
                            addinfo = item.split('"address-line\\">')[1].split(
                                "</div>"
                            )[0]
                            if addinfo.count("<br/>") == 1:
                                add = addinfo.split("<")[0]
                                city = item.split("<br/>")[1].split(",")[0]
                                state = (
                                    item.split("<br/>")[1]
                                    .split(",")[1]
                                    .strip()
                                    .split(" ")[0]
                                )
                                zc = (
                                    item.split("<br/>")[1]
                                    .split(",")[1]
                                    .strip()
                                    .split("<")[0]
                                    .rsplit(" ", 1)[1]
                                )
                            else:
                                add = (
                                    addinfo.split("<")[0]
                                    + " "
                                    + addinfo.split("<br/>")[1].strip()
                                )
                                city = item.split("<br/>")[2].split(",")[0]
                                state = (
                                    item.split("<br/>")[2]
                                    .split(",")[1]
                                    .strip()
                                    .split(" ")[0]
                                )
                                zc = (
                                    item.split("<br/>")[2]
                                    .split(",")[1]
                                    .strip()
                                    .split("<")[0]
                                    .rsplit(" ", 1)[1]
                                )
                            phone = item.split('<a href=\\"tel:')[1].split("\\")[0]
                            hours = "<MISSING>"
                            lurl = item.split('title field-link\\"><a href=\\"')[
                                1
                            ].split('\\"')[0]
                            country = "US"
                            typ = item.split('\\"line-of-business\\">')[1].split("<")[0]
                            store = item.split('"')[0]
                            if typ == "":
                                typ = "<MISSING>"
                            if phone == "":
                                phone = "<MISSING>"
                            lat = item.split('data-latlong=\\"')[1].split("|")[0]
                            lng = (
                                item.split('data-latlong=\\"')[1]
                                .split("|")[1]
                                .split("\\")[0]
                            )
                            if lat == "":
                                lat = "<MISSING>"
                                lng = "<MISSING>"
                            logger.info(lurl)
                            session = SgRequests()
                            time.sleep(7)
                            r3 = session.get(lurl, headers=headers)
                            if r3.encoding is None:
                                r3.encoding = "utf-8"

                            for line3 in r3.iter_lines(decode_unicode=True):
                                if "PM</td></tr>" in line3:
                                    try:
                                        hours = line3.split("<table><tr><td>")[1].split(
                                            "</td></tr></table>"
                                        )[0]
                                        hours = (
                                            hours.replace("</td></tr><tr><td>", "; ")
                                            .replace("<td>", "")
                                            .replace("</td>", "")
                                            .replace("</tr>", "")
                                            .replace("<tr>", "")
                                        )
                                    except:
                                        pass
                            yield [
                                website,
                                lurl,
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
                        except:
                            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
