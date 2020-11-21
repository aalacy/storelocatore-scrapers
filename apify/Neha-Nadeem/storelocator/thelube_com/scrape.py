from bs4 import BeautifulSoup
import csv
import time,re
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("thelube_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    data = []
    cleanr = re.compile(r'<[^>]+>')
    pattern = re.compile(r'\s\s+')
    url = "http://thelube.com/category/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("ul", {"class": "locationDetails"}).findAll(
        "li", {"class": "location"}
    )

    for div in divlist:
        link = div.find("a")["href"]
        title = div.find("h4").text
        address = div.find("span", {"class": "address"})
        store = div["id"].split("-")[1]
        phone = div.find("span", {"class": "phoneNum"}).text
        lat = div.find("span", {"class": "lat"}).text
        long = div.find("span", {"class": "long"}).text
        r1 = session.get(link, headers=headers, verify=False)
        soup1 = BeautifulSoup(r1.text, "html.parser")
        address = str(address)
        address = re.sub(pattern, ' ', address)
        address = address.split('>', 1)[1].split('</span', 1)[0].lstrip().split('<br/>')
        count = len(address)
        street = ' '.join(address[0:count - 1])
        city, state = address[-1].split(', ')
        state, pcode = state.lstrip().split(' ', 1)

        hourslist = soup1.find("li", {"class": "clockIcon"}).  text.splitlines()
        hours = ""
        for hr in hourslist:
            if hr.find("am") > -1 and hr.find("pm") > -1:
                hours = hours + hr + " "
        if len(hours) < 3:
            hours = "<MISSING>"

        b = "()"
        for char in b:
            phone = phone.replace(char, "")

        lat = lat.strip()
        long = long.strip()
        phone = phone.strip()
        store = store.strip()
        street = street.strip()
        street = street.replace(",", "")
        city = city.strip()
        city = city.replace(",", "")
        state = state.strip()
        state = state.replace(",", "")
        pcode = pcode.strip()
        pcode = pcode.replace(",", "")

        phone = re.sub(r'[A-Za-z*]', "", phone)
        phone1 = list(phone)

        try:
            if phone1[3] == " ":
               phone1[3] = "-"
        except:
            pass
        phone = ""
        for ele in phone1:
            phone += ele
        phone = phone.split(" ", 1)[0]

        if len(phone) > 12:
            phone = phone[-12:]

        if len(phone) == 0:
            phone = '<MISSING>'


        data.append(
            [
                "http://thelube.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                long,
                hours,
            ])

    return data


def scrape():

    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()