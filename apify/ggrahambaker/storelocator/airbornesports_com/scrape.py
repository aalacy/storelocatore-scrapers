from bs4 import BeautifulSoup
import csv
import usaddress


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
        for row in data:
            writer.writerow(row)


def fetch_data():

    data = []
    url = "https://airbornesports.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"id": "choose-location"}).findAll(
        "a", {"class": "fusion-button"}
    )
    p = 0
    for div in divlist:

        title = div.text
        if "airbornelewisville" in div["href"]:
            link = div["href"] + "contact"
        else:
            link = div["href"] + "contact-us"
        r = session.get(link, headers=headers, verify=False)
        try:
            address = (
                r.text.split('"address":"', 1)[1].split('"', 1)[0].replace(",", "")
            )
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
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("Recipient") != -1
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
            street = street.lstrip().replace(",", "")
            city = city.lstrip().replace(",", "")
            state = state.lstrip().replace(",", "")
            pcode = pcode.lstrip().replace(",", "")

            try:
                lat = r.text.split('"latitude":"', 1)[1].split('"', 1)[0]
                longt = r.text.split('"longitude":"', 1)[1].split('"', 1)[0]
            except:
                lat = longt = "<MISSING>"
            phone = hours = "<MISSING>"
        except:
            street = r.text.split('"addressLine1":"', 1)[1].split('"', 1)[0]
            city, state, pcode = (
                r.text.split('"addressLine2":"', 1)[1].split('"', 1)[0].split(", ")
            )
            lat = r.text.split('"mapLat":', 1)[1].split(",", 1)[0]
            longt = r.text.split('"mapLng":', 1)[1].split(",", 1)[0]
            phone = r.text.split('"contactPhoneNumber":"', 1)[1].split('"', 1)[0]
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
            hourslist = r.text.split('"businessHours":{', 1)[1].split(
                ',"storeSettings"', 1
            )[0]
            hourslist = hourslist.split('"text":"')
            hours = (
                "Monday "
                + hourslist[1].split('",', 1)[0]
                + " Tuesday "
                + hourslist[2].split('",', 1)[0]
                + " Wednesday "
                + hourslist[3].split('",', 1)[0]
                + " Thursday "
                + hourslist[4].split('",', 1)[0]
                + " Friday "
                + hourslist[5].split('",', 1)[0]
                + " Saturday "
                + hourslist[6].split('",', 1)[0]
                + " Sunday "
                + hourslist[7].split('",', 1)[0]
            )
        data.append(
            [
                "https://airbornesports.com/",
                link.replace("contact-us", "").replace("contact", ""),
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
                longt,
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
