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
    locator_domain = "https://www.vancity.com/"
    api_url = "https://www.vancity.com/rest/public/atm_branch/search?range=0%2C4999&filterOnBox=51.592557462750385%2C-127.64531054687498%2C48.08739145660382%2C-120.10868945312498&token=null&_=1616870794157"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()

    for j in js["results"]:
        branch = j.get("branches")
        if branch is not None:
            street_address = j.get("branches")[0].get("address").get("street")
            city = j.get("branches")[0].get("address").get("city")
            postal = j.get("branches")[0].get("address").get("pcode")
            state = j.get("branches")[0].get("address").get("prov")
            country_code = "Canada"
            store_number = j.get("branches")[0].get("branch")
            location_name = j.get("branches")[0].get("name")
            phone = "".join(j.get("branches")[0].get("phones")[0].get("num"))
            if phone.find("VAN") != -1:
                phone = "<MISSING>"
            latitude = j.get("location").get("lat")
            longitude = j.get("location").get("lon")
            location_type = "branch"
            hours = j.get("branches")[0].get("hours")[0]
            tmp = []
            for i in range(0, 7):
                day = hours.get("days")[i].get("label")
                try:
                    open = hours.get("days")[i].get("hours")[0].get("o")
                    close = hours.get("days")[i].get("hours")[0].get("c")
                    line = f"{day} {open} - {close}"
                    tmp.append(line)
                except TypeError:
                    line = f"{day} - Closed"
                    tmp.append(line)

            hours_of_operation = " ".join(tmp)
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "<Closed>"
            page_url = "https://www.vancity.com/ContactUs/FindBranchATM/"
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
