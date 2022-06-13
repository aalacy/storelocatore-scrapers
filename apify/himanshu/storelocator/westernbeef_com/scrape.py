from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "http://westernbeef.com/"
    r = session.get(
        "http://westernbeef.com/western-beef---locations.html", headers=headers
    )
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all(
        "a",
        {
            "class": "nonblock nontext Button rounded-corners transition clearfix grpelem"
        },
    )
    url = []
    for link in links:
        if base_url + link["href"] in url:
            continue
        url.append(base_url + link["href"])
        page_url = base_url + link["href"]
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.title.text
        if (
            "Address:"
            in soup1.find_all("div", {"data-muse-type": "txt_frame"})[-1].text
        ):
            data = list(
                soup1.find_all("div", {"data-muse-type": "txt_frame"})[
                    -1
                ].stripped_strings
            )
            street_address = data[1]
            city = data[2].split(",")[0]
            state = data[2].split(",")[1].split(" ")[1]
            zipp = data[2].split(",")[1].split(" ")[2]
            phone = data[-1].split(":")[-1].strip()
            hours_of_operation = " ".join(data[3:-2])

        elif (
            "Address:" in soup1.find_all("div", {"data-muse-type": "txt_frame"})[0].text
        ):
            data = list(
                soup1.find_all("div", {"data-muse-type": "txt_frame"})[
                    0
                ].stripped_strings
            )
            street_address = data[1]
            city = data[2].split(",")[0]
            state = data[2].split(",")[1].split(" ")[1]
            zipp = data[2].split(",")[1].split(" ")[2]
            phone = data[-1].split(":")[-1].strip()
            hours_of_operation = " ".join(data[3:-2])
        else:
            try:
                raw_data = soup1.find_all("img", {"class": "grpelem"})[1]["alt"]
            except:
                raw_data = soup1.find("img", {"class": "colelem"})["alt"]
            if "Telephone" in raw_data:
                phone = raw_data.split("Telephone :")[1].strip()
                hours_of_operation = (
                    "Hours:"
                    + " "
                    + raw_data.split("Hours:")[1].split("Contact")[0].strip()
                )
                street_address = (
                    raw_data.split("Hours:")[0]
                    .split(",")[0]
                    .split("Address:")[1]
                    .strip()
                )
                city = (
                    raw_data.split("Hours:")[0]
                    .split(",")[0]
                    .split("Address:")[1]
                    .split(" ")[-1]
                    .replace("Hempstead", "W. Hempstead")
                    .replace("Island", "Staten Island")
                    .replace("Ave", "Brooklyn")
                    .strip()
                )

                state = raw_data.split("Hours:")[0].split(",")[-1].split()[0].strip()
                zipp = raw_data.split("Hours:")[0].split(",")[-1].split()[1].strip()
            else:
                phone = "<MISSING>"
                hours_of_operation = "Hours:" + " " + raw_data.split("Hours:")[1]
                street_address = " ".join(
                    raw_data.split("Hours:")[0]
                    .split(",")[0]
                    .split("Address:")[1]
                    .split(" ")[:-1]
                )
                city = (
                    raw_data.split("Hours:")[0]
                    .split(",")[0]
                    .split("Address:")[1]
                    .split(" ")[-1]
                )
                state = raw_data.split("Hours:")[0].split(",")[1].split(" ")[1]
                zipp = raw_data.split("Hours:")[0].split(",")[1].split(" ")[2]

        street_address = street_address.replace(",", "").replace(city, "").strip()
        hours_of_operation = (
            hours_of_operation.replace("Hours:", "").split("Deli")[0].strip()
        )

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
