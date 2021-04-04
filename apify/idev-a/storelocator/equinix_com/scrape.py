import csv
from sgrequests import SgRequests
from urllib.parse import urljoin
import json

from util import Util  # noqa: I900

myutil = Util()


session = SgRequests()


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
    locator_domain = "https://www.equinix.com/data-centers/americas-colocation/"
    base_url = "https://www.equinix.com/api/marketo/buildjson?_=1611881724493"
    r = session.get(base_url)
    links = json.loads(r.text)["mapping-data"]
    data = []
    for key, value in links.items():
        if key.startswith(
            "/locations/americas-colocation/united-states-colocation/"
        ) or key.startswith("/locations/americas-colocation/canada-colocation/"):
            page_url = urljoin("https://www.equinix.com", key)
            if len(key.split("/")) == 6:
                continue
            _id = key.split("/")[-2]
            link = f"https://www.equinix.com/api/content/render/false/type/json/query/+contentType:Location%2520+Location.title:{_id}%2520+languageId:1%2520deleted:false%2520+working:true/orderby/modDate%2520desc"
            r1 = session.get(link)
            _location = json.loads(r1.text)
            if "contentlets" in _location and _location["contentlets"]:
                location = _location["contentlets"][0]
                location_name = location["popupLinkText"]
                street_address = ""
                city = ""
                state = ""
                zip = ""
                _split = location["address"].split(",")
                if "canada" in location["address"].lower():
                    street_address = "".join(_split[:-3])
                    country_code = "CA"
                    city = _split[-3].strip()
                    _state = myutil._strip_list(_split[-2].strip().split(" "))
                    state = _state[0].strip()
                    zip = " ".join(_state[1:]).strip()
                elif "canada" in location.get("description", "").lower():
                    street_address = "".join(_split[:-2]).strip()
                    country_code = "CA"
                    city = _split[-2].strip()
                    _state = myutil._strip_list(_split[-1].strip().split(" "))
                    state = _state[0].strip()
                    zip = " ".join(_state[1:]).strip()
                else:
                    if len(_split) == 1:
                        street_address = _split[0].split("\n")[0].strip()
                        city = "".join(
                            _split[0].split("\n")[-1].split(" ")[:-2]
                        ).strip()
                    elif len(_split) == 2:
                        street_address = (
                            _split[0].split("\n")[0].replace("<br>", "").strip()
                        )
                        if len(_split[0].split("\n")) > 1:
                            city = (
                                _split[0].split("\n")[-1].strip().split(" ")[-1].strip()
                            )
                        if len(_split[0].split("\n")) > 2:
                            street_address += " " + _split[0].split("\n")[-2]
                    else:
                        street_address = "".join(_split[:-1]).strip()
                        city = "".join(_split[-1].strip().split(" ")[:-2]).strip()
                        if not city:
                            if len(_split[1].split("\n")) > 1:
                                city = _split[1].split("\n")[1]
                                street_address = (
                                    _split[0]
                                    + _split[1]
                                    .split("\n")[0]
                                    .replace("<br>", "")
                                    .strip()
                                )
                            else:
                                city = _split[1].strip()
                    try:
                        _split1 = _split[-1].strip().split(" ")
                        state = _split1[-2].strip()
                        zip = _split1[-1].strip()
                        if len(_split) > 1 and len(_split1) >= 3:  # has city
                            city = " ".join(_split1[:-2])
                    except:
                        zip = _split[-1].strip()
                        state = _split[-2].strip()
                        street_address = _split[0].split("\n")[0].strip()
                        city = _split[0].split("\n")[1].strip()

                    country_code = myutil.get_country_by_code(state)
                phone = location.get("localSupport")
                if not phone:
                    phone = location.get("internationalSupport")
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                latitude = location["latitude"]
                longitude = location["longitude"]
                hours_of_operation = "<INACCESSIBLE>"

                data.append(
                    [
                        locator_domain,
                        page_url,
                        location_name,
                        street_address,
                        city,
                        state,
                        zip,
                        country_code,
                        store_number,
                        phone,
                        location_type,
                        latitude,
                        longitude,
                        hours_of_operation,
                    ]
                )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
