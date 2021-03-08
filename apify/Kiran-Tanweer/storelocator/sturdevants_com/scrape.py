import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("sturdevants_com")

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
    url = "https://www.sturdevants.com/wp-json/wpgmza/v1/datatables/base64eJy1kjFrwzAQhf9KuVlDknbSFjpkSWggLYXWpVysiy0qy+Z0NgWT-96z40Bo13qTnt77DnSvh6ZsHgOmBBZe95vd2zrLdshfxFufxMciy9auw5iTe8ZjIDCQBFnALgwEioWUYJcLvVTYfHqnmJV68jq0VVToew8OBUd7xIr0fUAQcl6OPCvckoGaHfGtcLGA7aHD0E45poK+wZ4wJDqfzZW9nJG9mpF9PyP74f-ZH1Ns3Oplw+PfO68SYMphsPwFvUQv5O4OgkLpN9XAyQch1qrtkbHSzvQq1h0xe0dTC5+GuQeS4Zyu0R-eGup6"
    stores_req = session.get(url, headers=headers).json()
    for store in stores_req["meta"]:
        title = store["title"]
        storeid = store["id"]
        address = store["address"]
        info = store["description"]
        address = address.split(",")
        if len(address) == 4:
            street = address[0].strip()
            city = address[1].strip()
            state = address[2].strip()
            country = address[3].strip()
        else:
            street = address[0].strip() + " " + address[1].strip()
            city = address[2].strip()
            state = address[3].strip()
            country = address[4].strip()
        if country.find("United States") != -1:
            country = country.replace("United States", "US")
        if any(char.isdigit() for char in country) == True:
            pcode = country.split(" ")[0]
            country = country.split(" ")[1]
        else:
            pcode = "<MISSING>"
        phone = info.split("<br />")[0]
        phone = phone.lstrip("<p>Phone: ")

        hours = info.split("<br />")[1].split("<a")[0].strip()
        hours = hours.lstrip("Hours: ")
        hours = hours.replace("&amp;", "&")
        hours = hours.replace("M-F", "Mon-Fri")

        link = "https://www.sturdevants.com" + info.split('href="')[1].split('"')[0]

        data.append(
            [
                "https://www.sturdevants.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                country,
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
