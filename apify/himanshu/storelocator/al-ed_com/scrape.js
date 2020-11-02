const Apify = require('apify');
const request = require('request');
const cheerio = require('cheerio');

async function scrape() {
    return new Promise(async(resolve, reject) => {
        var url = `https://al-ed.com/storelocator/index/loadstore?curPage=1`;
        request(url, async function(err, res, re) {
            if (!err && res.statusCode == 200) {
                var main = JSON.parse(res.body);
                var totpage = main.num_store;
                var page = 0;
                var r = Math.ceil(main.num_store / 10);
                var items = [];
                for (k = 1; k <= r; k++) {
                    url = `https://al-ed.com/storelocator/index/loadstore?curPage=` + k;
                    // console.log(url)
                    request(url, async function(err, res, re) {
                        if (!err && res.statusCode == 200) {
                            var main = JSON.parse(res.body);
                            var detail = main.storesjson;
                            for (const item of detail) {

                                var get_url = `https://al-ed.com/` + item.rewrite_request_path;
                                await request(get_url, function(err1, res1, body) {

                                    if (!err && res.statusCode == 200) {
                                        var $ = cheerio.load(body);
                                        var page_url = $(".fb-comments").attr('data-href')

                                        var address_tmp = item.address.split(',');

                                        if (address_tmp.length == 1) {
                                            address = address_tmp[0].trim();
                                            city = '<MISSING>';
                                            state = '<MISSING>';
                                            zip = '<MISSING>';
                                        } else if (address_tmp.length == 2) {

                                            city = item.store_name.trim().replace("Al & Ed’s Autosound", "").replace("Al & Ed's Autosound", "").replace("AE54 Al & Ed's W Hollywood/W", "").replace('West', '').trim();
                                            address = address_tmp[0].trim().replace(city, '').trim();
                                            state_tmp = address_tmp[1].trim().split(' ');
                                            state = state_tmp[0];
                                            zip = state_tmp[1];

                                        } else if (address_tmp.length == 3) {

                                            address = address_tmp[0].trim();
                                            city = address_tmp[1].trim();
                                            state_tmp = address_tmp[2].trim().split(' ');
                                            state = state_tmp[0];
                                            zip = state_tmp[1];

                                            // zip = madd[2].trim().split(' ')[1];
                                        }
                                        var hour = "Sunday : " + $('#open_hour table tbody tr').eq(0).find('td').eq(2).text() +
                                            " , Monday : " + $('#open_hour table tbody tr').eq(1).find('td').eq(2).text() +
                                            " , Tuesday : " + $('#open_hour table tbody tr').eq(2).find('td').eq(2).text() +
                                            " , Wednesday : " + $('#open_hour table tbody tr').eq(3).find('td').eq(2).text() +
                                            " , Thurday : " + $('#open_hour table tbody tr').eq(4).find('td').eq(2).text() +
                                            " , Friday : " + $('#open_hour table tbody tr').eq(5).find('td').eq(2).text() +
                                            " , Saturday : " + $('#open_hour table tbody tr').eq(6).find('td').eq(2).text();


                                        items.push({
                                            locator_domain: 'https://al-ed.com',
                                            location_name: item.store_name,
                                            street_address: address,
                                            city: city,
                                            state: state,
                                            zip: zip,
                                            country_code: 'US',
                                            store_number: item.storelocator_id,
                                            phone: item.phone,
                                            location_type: '<MISSING>',
                                            latitude: item.latitude,
                                            longitude: item.longitude,
                                            hours_of_operation: hour,
                                            page_url: page_url
                                        });
                                        page++;
                                        if (totpage == page) {
                                            resolve(items);
                                        }

                                    }
                                });

                            }
                        }
                    });
                }
            }
        })
    })
}
Apify.main(async() => {
    const data = await scrape();
    await Apify.pushData(data);

});