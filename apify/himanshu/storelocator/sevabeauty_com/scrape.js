const Apify = require('apify');
const request = require('request');
const cheerio = require('cheerio');


async function scrape() {

    return new Promise(async(resolve, reject) => {
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36',
        };

        var url = 'https://www.sevabeauty.com/location/locations.json';
        request({ headers: headers, uri: url }, (err, res, html) => {


            if (!err && res.statusCode == 200) {

                var ref = JSON.parse(res.body);

                var ref1 = ref.serviceAreas.serviceArea;

                var items = [];


                function mainhead(i)

                {
                    if (ref1.length > i)

                    {

                        var obj = ref1[i];
                        var address = obj._address;
                        var location_name = obj._name;
                        var city = obj._city;
                        var state = obj._state;
                        var zip = obj._zip;
                        var phone = obj._phone;
                        var longitude = obj._lng;
                        var lattitude = obj._lat;
                        var hour_temp = obj._hours;
                        var hour = hour_temp.replace(/<[^>]+>/g, ' ').trim().replace('Location Hours   Days  Hours   ', '').replace('    ', ' ');


                        items.push({
                            locator_domain: 'https://www.sevabeauty.com/',
                            location_name: location_name,
                            street_address: address,
                            city: city,
                            state: state,
                            zip: zip,
                            country_code: 'US',
                            store_number: '<MISSING>',
                            phone: phone,
                            location_type: '<MISSING>',
                            latitude: lattitude,
                            longitude: longitude,
                            hours_of_operation: hour,
                            page_url: '<MISSING>'
                        });


                        mainhead(i + 1);

                    } else {

                        resolve(items);

                    }
                }

                mainhead(0);

            }


        });
    });


}

Apify.main(async() => {

    const data = await scrape();

    await Apify.pushData(data);

});