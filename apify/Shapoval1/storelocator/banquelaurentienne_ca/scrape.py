import csv
from lxml import html
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

    locator_domain = "https://www.laurentianbank.ca/"
    api_url = "https://www.laurentianbank.ca/en/map/localizer.sn"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//table[@class="table_liste_succ"]//tr[./td]')

    for d in div:

        page_url = "https://www.laurentianbank.ca/en/map/localizer.sn"
        location_name = (
            " ".join(d.xpath(".//td[1]/text()"))
            .replace("(Gréber)", "Gréber")
            .replace("(Du Plateau)", "Du Plateau")
            .replace("(Place de la Cité)", "Place de la Cité")
            .replace("(Nord)", "Nord")
            .replace("\n", "")
            .strip()
        )
        location_name = (
            location_name.replace("branch branch", "branch").replace(">", "").strip()
        )
        ad = (
            " ".join(d.xpath(".//td[2]/text()"))
            .replace("\n", "")
            .replace("305,", "305")
            .strip()
        )
        if location_name.find("ABM outside branch") != -1:
            continue
        location_type = "Branch"
        street_address = ad.split(",")[0].strip()
        if street_address.find("500 Sacré-Cur St. West") != -1:
            street_address = "500 Sacré-Cœur St. West"

        if not street_address:
            continue
        state = ad.split(",")[1].split()[-1].strip()
        postal = ad.split(",")[-1].strip()
        country_code = "CA"
        city = " ".join(ad.split(",")[1].split()[:-1])
        if ad.count(",") == 3:
            street_address = ad.split(",")[0] + "" + ad.split(",")[1]
            city = " ".join(ad.split(",")[2].split()[:-1])
            state = ad.split(",")[2].split()[-1].strip()
        if location_name.find("Business Services Montérégie") != -1:
            street_address = "3400 de L’Éclipse St., Suite 610"
        store_number = "<MISSING>"
        if location_name.find("(") != -1:
            store_number = location_name.split("(")[1].split(")")[0].strip()
        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()

        phone = (
            "".join(d.xpath(".//td[3]/text()"))
            .replace("Toll Free", "")
            .replace(":", "")
            .strip()
        )
        if phone.find("ext") != -1:
            phone = phone.split("ex")[0].strip()

        hours_of_operation = d.xpath(".//td[4]/text()")
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
        if hours_of_operation.count("Appointment only") > 4:
            hours_of_operation = "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("Available 24 a day, 7 days a week", "")
            .replace("Fermé-Closed", "Closed")
            .strip()
        )
        slug = (
            ad.split(",")[0]
            .replace("305 King Street West", "305, King Street West")
            .replace("500 Sacré-Cur St. West", "500 Sacré-Cœur St. West")
            .replace("3400 de LÉclipse St.", "3400 de L’Éclipse St")
        )
        session = SgRequests()
        r = session.get(
            "https://www.laurentianbank.ca/en/map/map_api3.js?t=1624119221",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        marker = (
            "".join(tree.xpath("//*//text()"))
            .split(f"{slug}")[1]
            .split("open(map,")[1]
            .split(")")[0]
            .strip()
        )

        try:
            latitude = (
                "".join(tree.xpath("//*//text()"))
                .split(f"{marker}")[1]
                .split("LatLng(")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath("//*//text()"))
                .split(f"{marker}")[1]
                .split("LatLng(")[1]
                .split(",")[1]
                .split(")")[0]
                .strip()
            )

        except:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
