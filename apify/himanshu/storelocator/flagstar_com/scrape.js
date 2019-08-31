const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
async function scrape(){
    return new Promise(async (resolve,reject)=>{
        request('https://www.flagstar.com/flagstar-bank-branches-michigan.html',(err,res,html)=>{
            if(!err && res.statusCode==200){
                const $  =cheerio.load(html);
                var items=[];
                var main = $('#branchlist-resultstable tbody').children();
                var totpage=main.length;
                var page=0;
                main.each(function(index){  
                    var longitude =  $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).attr('data-longitude');
                    var lattitude = $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).attr('data-lattitude');
                    var link = $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).find('td').find('a').attr('href');  
                    var link_split_dot = link.split(".");
                    var link1_split_index =link_split_dot[link_split_dot.length-2];
                    var link_split_dash = link1_split_index.split("-");
                    var store_number = link_split_dash[link_split_dash.length-1];
                    var location_name =  $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).find('td').eq(0).text();    
                    var address =  $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).find('td').eq(1).text();    
                    var city =  $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).find('td').eq(2).text();    
                    var state =  $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).find('td').eq(3).text();    
                    var zip =  $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).attr('data-zip');    
                    var phone =  $('#branchlist-resultstable tbody').find('#branch-'+(index+1)).attr('data-bankingphone');
                    request(link,(err,res,html)=>{    
                        page++;
                        if(!err && res.statusCode==200){
                            var $ =cheerio.load(html);
                            var hours_branch =  $('#parent-container').find('#hours_branch').find('div[itemprop="openingHours"]').text().trim();
                            var hours_drive_thru =  $('#parent-container').find('#hours_drive_thru').find('div[itemprop="openingHours"]').text().trim();
                            var temp_hours_atm = $('#parent-container').find('#hours_atm').find('.card__details').text().trim();
                            var hours_atm_temp = temp_hours_atm.replace(/ +(?= )/g, "").replace(/\n+/g, "");
                            var hours_atm = hours_atm_temp.replace("ATM", " ");
                            var hour = hours_branch.concat(hours_drive_thru,hours_atm);
                            items.push({
                                locator_domain : 'https://www.flagstar.com',
                                location_name : location_name,
                                street_address : address,
                                city:city,
                                state:state,
                                zip:zip,
                                country_code: 'US',
                                store_number:store_number,
                                phone:phone,
                                location_type:'flagstarbank',
                                latitude :lattitude,
                                longitude:longitude,
                                hours_of_operation:hour
                            });
                            if(totpage==page)
                                resolve(items);
                        }//inner if 200
                    });//inner link req
        
                });
            }//if 200
        });
    })
}
Apify.main(async () => {
    
    const data = await scrape();
    await Apify.pushData(data);
});
