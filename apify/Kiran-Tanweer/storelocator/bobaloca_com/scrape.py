from bs4 import BeautifulSoup
import csv
import re
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bobaloca_com")

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
}

headers2 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "vsettings=; ASPSESSIONIDCCRQCQBB=MMHNFGOBGCCFHNKOLHOLFLEH; __utmc=243015313; __utmz=243015313.1612470565.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); TS014fe2d9=014f69ac9bb4b600b4640d99619ddfbcc4e39ffcac402a528114746aee674761a19bf0641e889bcc802b05171e0f035d3371bcc20ad5df7b7622fff5c63934e44b4fad2031a4d5f18bcce685d0ade350da8bf827f5; __utma=243015313.40972753.1612470565.1612470565.1612477242.2",
    "Host": "www.bobaloca.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "http://www.bobaloca.com/v/vspfiles/templates/223/Menu_Popout_Data.js"
    r = session.get(url, headers=headers, verify=False)
    soups = BeautifulSoup(r.text, "html.parser")
    links = str(soups)
    links = links.split("url=")
    for link in links:
        if link.find("http://www.bobaloca.com/") != -1:
            link = link.split(";")[0]
            r = session.get(link, headers=headers2, verify=False)
            soups = BeautifulSoup(r.text, "html.parser")
            title = soups.find("meta", {"name": "description"})["content"]
            table = soups.findAll("table")[1].findAll("span")

            if len(table) > 23:
                address = table[8].text + " " + table[11].text
                phone = table[14].text
                hours = (
                    table[9].text
                    + " "
                    + table[10].text
                    + " "
                    + table[12].text
                    + " "
                    + table[13].text
                    + " "
                    + table[15].text
                    + " "
                    + table[16].text
                    + " "
                    + table[18].text
                )

            else:
                if link == "http://www.bobaloca.com/category_s/1850.htm":
                    address = table[6].text
                    phone = table[9].text
                    hours = (
                        table[4].text
                        + " "
                        + table[5].text
                        + " "
                        + table[7].text
                        + " "
                        + table[8].text
                        + " "
                        + table[10].text
                        + " "
                        + table[11].text
                        + " "
                        + table[13].text
                    )
                if link == "http://www.bobaloca.com/category_s/1851.htm":
                    address = table[3].text + " " + table[6].text
                    phone = table[9].text
                    hours = (
                        table[4].text
                        + " "
                        + table[5].text
                        + " "
                        + table[7].text
                        + " "
                        + table[8].text
                        + " "
                        + table[10].text
                        + " "
                        + table[11].text
                        + " "
                        + table[13].text
                    )
                if link == "http://www.bobaloca.com/Boba_Loca_Gilroy_s/1857.htm":
                    address = table[7].text + " " + table[10].text
                    phone = table[13].text
                    hours = (
                        table[8].text
                        + " "
                        + table[9].text
                        + " "
                        + table[11].text
                        + " "
                        + table[12].text
                        + " "
                        + table[14].text
                        + " "
                        + table[15].text
                        + " "
                        + table[17].text
                    )

                if link == "http://www.bobaloca.com/Montrose_Boba_Loca_s/1852.htm":
                    address = table[6].text + " " + table[9].text
                    phone = table[12].text
                    hours = (
                        table[7].text
                        + " "
                        + table[8].text
                        + " "
                        + table[10].text
                        + " "
                        + table[11].text
                        + " "
                        + table[13].text
                        + " "
                        + table[14].text
                        + " "
                        + table[16].text
                    )

                if (
                    link
                    == "http://www.bobaloca.com/North_Hollywood_Boba_Loca_s/1830.htm"
                ):
                    address = table[8].text + " " + table[11].text
                    phone = table[14].text
                    hours = (
                        table[9].text
                        + " "
                        + table[10].text
                        + " "
                        + table[12].text
                        + " "
                        + table[13].text
                        + " "
                        + table[15].text
                        + " "
                        + table[16].text
                        + " "
                        + table[18].text
                    )

                if link == "http://www.bobaloca.com/West_Covina_Boba_Loca_s/1839.htm":
                    address = table[8].text + " " + table[11].text
                    phone = table[14].text
                    hours = (
                        table[9].text
                        + " "
                        + table[10].text
                        + " "
                        + table[12].text
                        + " "
                        + table[13].text
                        + " "
                        + table[15].text
                        + " "
                        + table[16].text
                        + " "
                        + table[18].text
                    )

                if (
                    link
                    == "http://www.bobaloca.com/WOODLAND_HILLS_BOBA_LOCA_s/1853.htm"
                ):
                    address = table[8].text + " " + table[11].text
                    phone = table[14].text
                    hours = (
                        table[9].text
                        + " "
                        + table[10].text
                        + " "
                        + table[12].text
                        + " "
                        + table[13].text
                        + " "
                        + table[15].text
                        + " "
                        + table[16].text
                        + " "
                        + table[18].text
                    )

            if address == "1843 Willow Pass RdConcord, CA 94520":
                address = "1843 Willow Pass Rd Concord, CA 94520"

            address = address.replace(",", " ")
            address = usaddress.parse(address)

            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1
            street = street.lstrip()
            street = street.replace(",", "")
            city = city.lstrip()
            city = city.replace(",", "")
            state = state.lstrip()
            state = state.replace(",", "")
            pcode = pcode.lstrip()
            pcode = pcode.replace(",", "")

            phone = phone.lstrip("Tel. ").strip()
            phone = phone.lstrip("Tel ").strip()
            hours = hours.replace(".", "").strip()
            hours = hours.replace("day", "day: ").strip()
            hours = hours.replace("pm", "pm,").strip()
            hours = re.sub(pattern, " ", hours)
            hours = re.sub(cleanr, " ", hours)

            storeid = link.split("/")[-1]
            storeid = storeid.rstrip(".htm")

            data.append(
                [
                    "http://www.bobaloca.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    storeid,
                    phone,
                    "<MISSING>",
                    "<INACCESSIBLE>",
                    "<INACCESSIBLE>",
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
