import csv
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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
    out = []

    locator_domain = "https://www.nautilusplus.com/"
    api_url = "https://www.nautilusplus.com/content/themes/nautilus/ajax/ajax-apinautilusplus.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    data = {"action": "GetBranches"}

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["data"]["Branches"]

    for j in js:
        a = j.get("Address")
        location_name = j.get("Description")

        location_type = "gym"
        street_address = a.get("StreetAndNumber")
        phone = a.get("PhoneNumber")
        state = a.get("Province")
        postal = a.get("PostalCode")
        country_code = a.get("Country")
        city = a.get("City")
        page_url = (
            f"https://www.nautilusplus.com/gym/{str(location_name).lower()}".replace(
                "é", "e"
            )
            .replace("è", "")
            .replace(" ", "-")
        )
        store_number = j.get("BranchNumber")
        if store_number == "990":
            continue
        latitude = a.get("Lat")
        longitude = a.get("Lng")
        if latitude == 0:
            latitude = "<MISSING>"
        if longitude == 0:
            longitude = "<MISSING>"
        if "3550" in street_address:
            location_type = "Head office"
        hours = j.get("BusinessHours")
        tmp = []
        for h in hours:
            days = (
                str(h.get("DayOfWeek"))
                .replace("1", "Monday")
                .replace("2", "Tuesday")
                .replace("3", "Wednesday")
                .replace("4", "Thursday")
                .replace("5", "Friday")
                .replace("6", "Saturday")
                .replace("7", "Sunday")
            )
            opens = h.get("OpeningHour")
            closes = h.get("ClosingHour")
            line = f"{days} {opens}-{closes}".replace("PT", "").strip()
            tmp.append(line)
            closeAllDay = h.get("ClosedAllDay")
            if closeAllDay == "true":
                line = f"{days} Close"
                tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if location_type == "Head office":
            hours_of_operation = "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
