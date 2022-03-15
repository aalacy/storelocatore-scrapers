import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
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
    titlelist = []
    p = 0

    url = "https://hosted.where2getit.com/crossroadstreatmentcenters/rest/getlist?lang=en_US&like=0.9440629796670679"
    myobj = {
        "request": {
            "appkey": "759DF48A-4A2C-11EB-9136-BE0593322438",
            "formdata": {"objectname": "Account::State", "where": {"country": "US"}},
        }
    }
    statelist = session.post(url, headers=headers, verify=False, json=myobj).json()[
        "response"
    ]["collection"]
    for state in statelist:
        state = state["name"]
        url = "https://hosted.where2getit.com/crossroadstreatmentcenters/rest/getlist?like=0.8777578110859998&lang=en_US"
        myobj = {
            "request": {
                "appkey": "759DF48A-4A2C-11EB-9136-BE0593322438",
                "formdata": {
                    "order": "city",
                    "objectname": "Locator::Store",
                    "where": {
                        "state": {"eq": state},
                        "methadone": {"in": ""},
                        "suboxone": {"in": ""},
                    },
                },
            }
        }

        loclist = session.post(url, headers=headers, verify=False, json=myobj).json()[
            "response"
        ]["collection"]

        for loc in loclist:

            title = loc["name"]
            street = loc["address1"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["postalcode"]
            phone = loc["phone"]
            try:
                if len(phone) < 3:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"
            lat = loc["latitude"]
            longt = loc["longitude"]
            try:
                if "Call" in loc["hours"]:
                    hours = "<MISSING>"
                else:
                    hours = (
                        "Monday "
                        + loc["mondayhours"]
                        + " Tuesday "
                        + loc["tuesdayhours"]
                        + " Wednesday "
                        + loc["wednesdayhours"]
                        + " Thursday "
                        + loc["thursdayhours"]
                        + " Friday "
                        + loc["fridayhours"]
                        + " Saturday "
                        + loc["saturdayhours"]
                        + " Sunday "
                        + loc["sundayhours"]
                    )
            except:
                hours = "<MISSING>"
            link = (
                "https://locations.crossroadstreatmentcenters.com/"
                + state.lower()
                + "/"
                + city.lower()
                + "/"
                + str(loc["clientkey"]).lower()
            )
            if link in titlelist or (phone == "<MISSING>" and hours == "<MISSING>"):
                continue
            titlelist.append(link)
            if True:
                data.append(
                    [
                        "https://www.crossroadstreatmentcenters.com/",
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
                        str(loc["clientkey"]),
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
