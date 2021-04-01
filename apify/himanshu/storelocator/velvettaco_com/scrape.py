import csv
from sgrequests import SgRequests
import lxml.html
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("velvettaco_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def getDecodedPhoneNo(encoded_phone_no):
    _dict = {}
    _dict["2"] = "ABC"
    _dict["3"] = "DEF"
    _dict["4"] = "GHI"
    _dict["5"] = "JKL"
    _dict["6"] = "MNO"
    _dict["7"] = "PQRS"
    _dict["8"] = "TUV"
    _dict["9"] = "WXYZ"

    _real_phone = ""
    for _dg in encoded_phone_no:
        for key in _dict:
            if _dg in _dict[key]:
                _dg = key
        _real_phone += _dg
    return _real_phone


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://velvettaco.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = lxml.html.fromstring(r.text)
    return_main_object = []

    k = soup.xpath('//div[@id="location_drop"]//a')
    for i in k:
        tem_var = []
        page_url = "".join(i.xpath("@href")).strip()
        logger.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = lxml.html.fromstring(r.text)
        script = soup.xpath('//script[@type="application/ld+json"]/text()')[-1]
        script = script.rsplit("}", 1)[0].strip()
        if script[-1] == ",":
            script = "".join(script[:-1]).strip() + "}"
        else:
            script = script + "}"

        store_json = json.loads(script.strip())
        address = store_json["address"]["streetAddress"]
        contry = store_json["address"]["addressCountry"]
        city = store_json["address"]["addressLocality"]
        state = store_json["address"]["addressRegion"]
        zip1 = store_json["address"]["postalCode"]
        streetAddress = (
            address.replace(city, "")
            .replace(state, "")
            .replace(zip1, "")
            .replace(" ,", "")
        )
        phone1 = "<MISSING>"
        if "telephone" in store_json:
            phone = store_json["telephone"]
            phone1 = getDecodedPhoneNo(phone)

        name = store_json["name"]
        openingHours = "<MISSING>"
        if "openingHours" in script:
            openingHours = " ".join(store_json["openingHours"])

        location_type = "".join(
            soup.xpath('//div[@class="coming_soon"]/text()')
        ).strip()
        if len(location_type) <= 0:
            location_type = "<MISSING>"

        tem_var.append("https://velvettaco.com")
        tem_var.append(name)
        tem_var.append(streetAddress)
        tem_var.append(city)
        tem_var.append(state.strip() if state.strip() else "<MISSING>")
        tem_var.append(zip1)
        tem_var.append(contry)
        tem_var.append("<MISSING>")
        tem_var.append(phone1)
        tem_var.append(location_type)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(openingHours)
        tem_var.append(page_url)
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
