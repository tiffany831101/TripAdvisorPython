
var cur_page=1; //當前頁
var next_page=1;//下一頁
var total_page=1; //總頁數
var house_data_querying = true; //是否正在向後台獲取數據
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    },{});
}
//更新房源列表信息
//action表示從後端請求的數據在前端的展示方式
// 默認採取追加方式
// action =renew 代表頁面數據清空重新展示

function updateHouseData(action) {
    var areaId = $(".filter-area">li.active).attr("area-id");
    if (undefined ==areaId) areaId="";
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var sortKey = $(".filter-sort">li.active).attr("sort-key");
    var params = {
        aid=areaId,
        sd:startDate,
        ed:endDate,
        sk:sortKey,
        p:next_page
    };
    $.get("/api/v1.0/houses", params, function(resp){
        house_date_querying=false;
        if ("0"==resp.errno){
            if(0==resp.data.total_page){
                $(".house-list").html("暫時沒有符合您查詢的房屋信息");
            } else{
                total_page = resp.data.total_page;
                if ("renew"==action) {
                    cur_page = 1;
                    $(".house-list").html(template("house-list-tmpl",{houses:resp.data.houses}))
                } else{
                    cur_page = next_page;
                    $(".house-list").append(template("house-list-tmpl",{houses:resp.data.houses}))

                }
            }
        }
    })
}

$(document).ready(function(){
    var queryData = descodeQuery();
    var startDate = queryData["sd"];
    var endDate = queryData["ed"];
    $("#start-date").val(startDate);
    $("#end-date").val(endDate)
    updateFilterDateDisplay();
    var areaName = queryData["aname"];
    if (!areaName) areaName ="位置區域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);
})

//獲取篩選條件中的城市區域信息
$.get("api/v1.0/areas", function(data){
    if ("0" ==data.errno){
        // 用戶從首頁跳轉到這個搜索夜宴時可能選擇了城區，所以嘗試從url查詢字符串參數中提取用戶選擇的城區
        var areaId=queryData["aid"];
        //如果提取到了城區id的數據
        if(areaId){
            //便利從後端獲取到的城區信息，添加到頁面中
            for (var i=0, i < data.data.length; i++){
                areaId=parseInt(areaId);
                if (data.data[i].aid ==areaId){
                    $(".filter-area").append('<li area-id="'+data.data[i].aid+'"')
                }else{
                    $(".filter-area").append('<li area-id="'+data.data[i].aid+'"')
                }
            }
        }else{

        }
    }
})