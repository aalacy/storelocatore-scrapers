import csv
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

website = "vanheusen_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    data = []
    zips = static_zipcode_list(radius=100, country_code=SearchableCountries.USA)
    if True:
        for zip_code in zips:
            url = "https://secure.gotwww.com/gotlocations.com/vanheusendev/index.php"
            myobj = {"address": zip_code}
            r = session.post(url, data=myobj, headers=headers)
            if "L.marker" not in r.text:
                continue
            loclist = r.text.split("L.marker(")[1:]
            for loc in loclist:
                coords = loc.split(", {icon: customIcon}", 1)[0]
                coords = coords.split(",")
                lat = coords[0].split("[", 1)[1]
                longt = coords[1].split("]", 1)[0]
                temploc = (
                    loc.split("numtoshow.push", 1)[0]
                    .split(".bindPopup('", 1)[1]
                    .split("');", 1)[0]
                )
                title = temploc.split('<div class="maptexthead">', 1)[1].split(
                    "</div>", 1
                )[0]
                title = title.split("  ", 1)[0]

                templist = temploc.split("<br>")[1:5]
                if "US" not in templist[2]:
                    continue
                street = templist[0]
                city = templist[2].split(",", 1)[0]
                state = templist[2].split(",", 1)[1].replace("US", "").strip()
                tempzip = "+" + state + "," + "+"
                pcode = temploc.split(tempzip, 1)[1].split(",+US", 1)[0]
                phone = templist[3].split("Phone:", 1)[1].strip()
                data.append(
                    [
                        "https://vanheusen.partnerbrands.com/en",
                        "https://vanheusen.partnerbrands.com/en/customerservice/store-locator",
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
                        "<MISSING>",
                    ]
                )
        return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
