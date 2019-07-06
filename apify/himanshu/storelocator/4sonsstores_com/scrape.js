const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
async function scrape() {
  return new Promise(async (resolve,reject)=>{
    var url=`http://4sonsstores.com/2-top-tier-fuel.html`;
    request(url,async function(err,res,body){
      if(!err && res.statusCode==200){
        var $=cheerio.load(body);
        var items=[];
        var temp_index = $('map').children().length;
        var temp_cnt = 0;
        $('map').children().each( async function(index)
        {
            var data=$('map').children('area').eq(index).attr('href');
            var url1=`http://4sonsstores.com/`+data;
            await request(url1,function(err1,res1,body1){
                if(!err1 && res1.statusCode==200){
                    var $1=cheerio.load(body1);
                    var main=$1('#table3 tbody tr td table tbody tr td table tbody tr td').children().eq(0).find('tbody');
                    var store=main.find('tr').eq(0).find('span span').text().split('Store ')[1];
                    var mainaddress=main.find('tr').eq(1).find('td').find('span').not(0).text();
                    var minadd=main.find('tr').eq(1).find('td').text().replace(/\n+/g, '').replace(/\n+/g, '');
                    var i=minadd.indexOf(')');
                    var i1=minadd.indexOf(',');
                    var name=minadd.substring(0,i+1).replace(/  +/g, ' ');
                    var address=minadd.substring(i+1,i1);
                    var sd1=minadd.substring(i1).replace(", ",'').split('PHONE: ');
                    var state=sd1[0].substring(0,2).trim();
                    var zip=sd1[0].substring(3,).trim();
                    var phone=sd1[1].split('FAX:')[0];
                    items.push({
                        locator_domain: 'http://4sonsstores.com',
                        location_name:name.replace(/(\n|\s\s)+/g, " "),
                        street_address: "<INACCESSIBLE>",
                        raw_address: address,
                        city:"<INACCESSIBLE>",
                        state: state,
                        zip: parseFloat(zip),
                        country_code: 'US',
                        store_number:store,
                        phone:phone,
                        location_type: '4sonsstores',
                        latitude: '<MISSING>',
                        longitude: '<MISSING>',
                        hours_of_operation: '<MISSING>'
                    });
                    temp_cnt++;
                    if(temp_cnt==temp_index){
                        resolve(items);
                    }
                }
            })
            
        });
      }
    })
  })
}

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});
