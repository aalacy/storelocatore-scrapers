import json
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):

    base_link = "https://www.mitsubishicars.com/car-dealerships-near-me"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests(verify_ssl=False)
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    base_url = "https://www.mitsubishicars.com/"
    addressess = []

    fin_script = ""
    all_scripts = base.find_all("script")
    for script in all_scripts:
        if 'addressLine1":' in str(script):
            fin_script = str(script)
            break
    js = fin_script.split("__ =")[2].split("; window")[0]
    store_data = json.loads(js)

    for i in store_data:
        if i[:7] == "Dealer_":
            store = store_data[i]
            phone_det = store_data["$" + i + ".phone"]
            add_det = store_data["$" + i + ".address"]

            name = store["name"]
            address = add_det["addressLine1"]
            city = add_det["addressLine2"]
            try:
                state = add_det["addressLine3"]
            except:
                state = ""
            zipp = add_det["postalArea"]
            phone = phone_det["phoneNumber"]
            country = "US"
            lat = add_det["latitude"]
            lng = add_det["longitude"]
            page_url = store["url"]
            storeno = store["id"]
            if page_url:
                print(page_url)
                if (
                    "http://www.verneidemitsubishi.com" in page_url
                    or "http://www.kingautomitsubishi.com" in page_url
                    or "http://www.verhagemitsubishi.com" in page_url
                    or "http://www.sisbarro-mitsubishi.com" in page_url
                    or "http://www.delraymitsu.net" in page_url
                ):
                    hours_of_operation = "<INACCESSIBLE>"
                else:
                    try:
                        r1 = session.get(page_url, headers=headers)
                        soup1 = BeautifulSoup(r1.text, "lxml")
                        got_page = True
                    except:
                        got_page = False
                    if got_page:
                        if soup1.find("div", {"class": "sales-hours"}):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find(
                                        "div", {"class": "sales-hours"}
                                    ).stripped_strings
                                )
                            )
                        elif soup1.find(
                            "ul", {"class": "list-unstyled line-height-condensed"}
                        ):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find(
                                        "ul",
                                        {
                                            "class": "list-unstyled line-height-condensed"
                                        },
                                    ).stripped_strings
                                )
                            )
                        elif soup1.find("div", {"class": "well border-x"}):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find("div", {"class": "well border-x"})
                                    .find("table")
                                    .stripped_strings
                                )
                            )
                        elif soup1.find("div", {"class": "hours-block pad-2x"}):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find(
                                        "div", {"class": "hours-block pad-2x"}
                                    ).stripped_strings
                                )
                            )
                        elif soup1.find("div", {"class": "hoursBox"}):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find(
                                        "div", {"class": "hoursBox"}
                                    ).stripped_strings
                                )
                            )
                        else:
                            hours_of_operation = "<INACCESSIBLE>"
                    else:
                        hours_of_operation = "<INACCESSIBLE>"

            store = []
            store.append(base_url)
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country)
            store.append(storeno)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            try:
                store.append(hours_of_operation.split("Sales Hours")[1].strip())
            except:
                store.append(hours_of_operation)
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            store = [
                str(x)
                .encode("ascii", "replace")
                .decode("ascii")
                .strip()
                .replace("?", "")
                if x
                else "<MISSING>"
                for x in store
            ]
            sgw.write_row(
                SgRecord(
                    locator_domain=store[0],
                    location_name=store[1],
                    street_address=store[2],
                    city=store[3],
                    state=store[4],
                    zip_postal=store[5],
                    country_code=store[6],
                    store_number=store[7],
                    phone=store[8],
                    location_type=store[9],
                    latitude=store[10],
                    longitude=store[11],
                    hours_of_operation=store[12],
                    page_url=store[13],
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
