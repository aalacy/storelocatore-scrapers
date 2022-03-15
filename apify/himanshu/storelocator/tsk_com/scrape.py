import json

from sgrequests import SgRequests
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://tsk.com/locations/"

    session = SgRequests(verify_ssl=False)
    req = session.get(base_link, headers=headers)
    soup = BeautifulSoup(req.text, "lxml")

    all_scripts = soup.find_all("script")
    for script in all_scripts:
        if "var locations = " in str(script):
            script = str(script)
            break

    main = script.split("var locations = ")[1].split("}]];\n")[0] + "}]]"
    list_1 = []
    data_json = json.loads(main)
    for i in data_json:
        for j in i:
            list_1.append(j)
    try:
        i = 4
        while True:
            store = []
            store.append("https://tsk.com/")
            store.append(list_1[i]["name"] if list_1[i]["name"] else "<MISSING>")
            store.append(list_1[i]["street"] if list_1[i]["street"] else "<MISSING>")
            store.append(list_1[i]["city"] if list_1[i]["city"] else "<MISSING>")
            store.append(list_1[i]["state"] if list_1[i]["state"] else "<MISSING>")
            store.append(list_1[i]["zip5"] if list_1[i]["zip5"] else "<MISSING>")
            store.append("US")
            store.append(list_1[i]["crmSchoolId"])
            store.append(list_1[i]["phone"] if list_1[i]["phone"] else "<MISSING>")
            store.append("")
            store.append(list_1[i]["lat"] if list_1[i]["lat"] else "<MISSING>")
            store.append(list_1[i]["lon"] if list_1[i]["lon"] else "<MISSING>")

            link = "https://tsk.com/locations" + list_1[i]["url"]
            req = session.get(link, headers=headers)
            soup = BeautifulSoup(req.text, "lxml")
            hours = ""
            tables = soup.find_all(
                class_="elementor-widget-wrap elementor-element-populated"
            )
            for table in tables:
                if "HOURS" in table.text.upper():
                    hours = (
                        " ".join(list(table.ul.stripped_strings))
                        .replace("   ", " ")
                        .replace("  ", " ")
                    )
            if hours.lower().count("soon") != 7 and hours.upper().count("TBD") != 7:
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
                        hours_of_operation=hours,
                        page_url=link,
                    )
                )

            i = i + 5
    except:
        pass


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
