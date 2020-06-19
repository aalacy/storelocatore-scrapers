const Apify = require('apify');
const request = require('request');
const cheerio = require('cheerio');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const csvWriter = createCsvWriter({
    path: 'data.csv',
    header: [
        { id: 'locator_domain', title: 'locator_domain' },
        { id: 'location_name', title: 'location_name' },
        { id: 'street_address', title: 'street_address' },
        { id: 'city', title: 'city' },
        { id: 'state', title: 'state' },
        { id: 'zip', title: 'zip' },
        { id: 'country_code', title: 'country_code' },
        { id: 'store_number', title: 'store_number' },
        { id: 'phone', title: 'phone' },
        { id: 'location_type', title: 'location_type' },
        { id: 'latitude', title: 'latitude' },
        { id: 'longitude', title: 'longitude' },
        { id: 'hours_of_operation', title: 'hours_of_operation' },
        { id: 'page_url', title: 'page_url' },
    ]
});

var url = 'https://www.tradewindsmarkets.com/locations/';

async function scrape() {
    return new Promise(async(resolve, reject) => {
        request(url, (err, res, html) => {

            if (!err && res.statusCode == 200) {

                const $ = cheerio.load(html);

                var items = [];
                var main = $('.locations-list').find('li');

                function mainhead(i) {

                    if (main.length > i)

                    {
                        var link = $(main[i]).find('a').attr('href');
                        // console.log(link);
                        // exit();
                        request(link, (err, res, html) => {
                            if (!err && res.statusCode == 200) {
                                const $ = cheerio.load(html);

                                var location_name = $('.interior-masthead').find('h1').text();

                                var phone = $('.primary').find('p').eq(0).text().trim();

                                // var latitude = $('.marker').attr('data-lat');

                                // var longitude = $('.marker').attr('data-lng');

                                var address_temp = $('.primary').find('p').eq(1).text().trim();

                                var address_temp1 = address_temp.split(',');
                                if (address_temp1.length == 4) {
                                    var address = address_temp1[0];
                                    var city = address_temp1[1];
                                    var state_temp = address_temp1[2];
                                    var state_temp1 = state_temp.split(' ');
                                    if (state_temp1.length == 3) {



                                        var state = state_temp1[1];

                                        var zip = state_temp1[2];



                                    } else {

                                        var state = state_temp1[1];

                                        var zip = '<MISSING>';

                                    }

                                } else if (address_temp1.length == 5) {

                                    var address = address_temp1[0];

                                    var city = address_temp1[2];

                                    var state = address_temp1[3];

                                    var zip = '<MISSING>';

                                }

                                items.push({

                                    locator_domain: 'https://www.tradewindsmarkets.com/',

                                    location_name: location_name,

                                    street_address: address,

                                    city: city,

                                    state: state,

                                    zip: zip,

                                    country_code: 'US',

                                    store_number: '<MISSING>',

                                    phone: phone,

                                    location_type: '<MISSING>',

                                    latitude: '<MISSING>',

                                    longitude: '<MISSING>',

                                    hours_of_operation: '<MISSING>',

                                    page_url: link


                                });
                                mainhead(i + 1);
                            }
                        });
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
    csvWriter
        .writeRecords(data)
        .then(() => console.log('The CSV file was written successfully'));

    await Apify.pushData(data);
});
