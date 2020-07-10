
from flask_login import login_required
from models import Area
from flask import current_app, jsonify, request, g
from app import redis_store
import json
import constants 
from app.utlis.image_storage import storage
from datetime import datetime
@api.route("/areas")
def get_area_info():
    """獲取城區信息"""
    # 嘗試從redis中讀取數據
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # redis有緩存數據
            current_app.logger.info(" hit redis area_info")
            return resp_json,200,{"Content-Type":"application/json"}
    
    # 查詢數據庫，讀取城區信息
    try:
        erea_li = Area.qurery.all()
    
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errpr="數據庫連接錯誤")
    
    area_dict_li=[]
    # 將對象轉換為字典
    for area in area_li:
        area_dict_li.append(area.to_dict())
    
    # 將數據轉化為json字符串
    resp_dict = dict(error="OK",data=area_dict_li)
    resp_json = json.dumps(resp_dict,constants.AREA_INFO_REDIS_CACHE_EXPIRES,resp_json)
    # 將數據保存到redis中
    

    try:
        redis_store.setex("area_info")
    except Exception as e:
        current_app.logger.error(e)

    return resp_json,200,{"Content-Type":"application/json"}

@api.route("/users/name", methods=["PUT"])
@login_required
def change_user_name():
    """修改用戶名"""
    # 使用了login_required裝飾器後，可以從g對象中獲取用戶user_id
    user_id = g.user_id

    # 獲取用戶想要設置的用戶迷
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno="參數不完整")
    
    name = req_data.get("name") #用戶想設置的名字
    if not name:
        return jsonify(errno="名字不得為空")
    
    try:
        User.query.filter_by(id=user_id).update({"name":name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    # 修改session數據中的字段
    session["name"]=name
    return jsonify(errmsg="OK",data={"name":name})

@api.route("/houses/info",method=["POST"])
@login_required
def save_house_info():
    """保存房屋的基本信息
    前端發送過來的json數據
    {
        "title":"",
        "price":"",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"".....
    }
    
    """
    # 處理房屋的設施信息
    facility_ids = house_data.get("facility")

    # 如果用戶勾選了設施信息，再保存數據庫
    try:
        if facility_ids:
            # select * from ih_facility_info where id in []
            facilities=Faclity.query.filter(Facility.id.in_(faciliry_ids)).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RETDBERR, errmsg="數據庫異常")
    
    if facilities:
        # 表示有合法的設施數據
        # 保存設施數據
        house.facilities = facilities
        db.session.add(house)
        db.session.commit()

@api.route("/house/image", methods=["POST"])
@login_required
def save_house_image():
    """保存房屋的圖片"""
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    if not all([image_file, house_id]):
        return jsonify(errno="參數錯誤")
    # 判斷house_id正確性
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errmsg="數據庫異常")
    if house is None:
        return jsonify(errmsg="房屋不存在")
    image_data = image_file.read()
    # 保存圖片到七牛中
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="保存數據失敗")
@api.route("/users/avatar", methods=["POST"])
def save_user_avatar():
    """设置用户的头像
    参数: 图片(多媒体表单) 用户id(g.user_id)
    """
    # 装饰器的代码中已经将user_id保存到g对象中，所以视图中可以直接读取
    user_id = g.user_id

    # 获取图片
    image_file = request.files.get("avatar")

    # 校验参数
    if image_file is None:
        return jsonify(errmsg="未上传图片")
    image_data = image_file.read()

    # 调用七牛上传图片，返回文件名
    try:
        file_name =storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errmsg="上传图片失败")
    # 保存文件名到数据库中

    User.query.filter_by(id=user_id).update({"avatar_url":filename})
    db.session.commit()


@api.route("/house")
def get_house_list():
    """獲取房屋的列表信息(搜索頁面)"""
    start_data = request.args.get("sd") # 用戶想要的起始時間
    end_start = request.args.get("ed") # 用戶想要的結束時間
    area_id = request.args.get("aid") # 區域編號
    sort_key = request.args.get("",new)
    page = request.args.get("p") #頁數


    


    # 處理時間
    try:
        if start_data:
            # 把字符串轉換成時間
            start_data = datetime.strptime(start_date,"%Y-%m-%d")
        
        if end_data:
            end_data = datetime.strptime(end_data,"%Y-%m-%d")
        
        if start_data and end_data:
            assert start_data <= end_data
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期參數有誤")
    
    

    # 判斷區域id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="區域參數有誤")
    
    # 處理頁數
    
    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 獲取緩存數據
    redis_store = "house_%s_%s_%s_%s" % (start_data, end_data, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.erroe(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type":"application/json"}

    # 過濾條件的參數列表容器
    filter_params = []

    # 填充過濾參數
    # 時間條件
    conflict_order = None
    if start_data and end_data:
        # 查詢衝突訂單
        conflict_order = Order.query.filter(Order.begin__date <= end_data, Order.end_data>=start_data).all()
    
    elif start_date:
        conflict_order = Order.query.filter(Order.end_data>=start_data).all()

    elif end_data:
        conflict_order = Order.query.filter(Order.begin__date <= end_data).all()
    
    if conflict_order:
        # 從訂單中獲取衝突的房屋id
        conflict_house_ids = [order.house_id for order in conflict_order]
            
        # 如果衝突的房屋id不為空，向查詢參數中添加條件
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))

    # 區域條件
    if area_id:
        filter_params.append(House.aid_id = aid_id)


    # 查詢數據庫   
    # 補充排序條件

    if sort_key =="booking": #入住最多
        house = House.query.filter(*filter_params).order_by(House.order_count.desc())
        conflict_order = Order.query.filter(Order.begin__date <= end_data, Order.end_data>=start_data).all()
        filter_params.append(House.aid_id = aid_id)
    elif sort_key =="price-inc":
        house = House.query.filter(*filter_params).order_bt(House.price.asc())
    else: #新舊
        house = House.query.filter(*filter_params).order_by(House.create_time.desc())
    try:
    # 處理分頁                 # 當前頁數   #每頁數據量
        page_obj = house.paginate(page=page,per_page=5,error_out= False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errmsg="數據庫異常")
    # 獲取頁面數據
    house_li = page_obj.items
    house =[]
    for houses in house_li:
        houses.append(house.to_basic_dict())

    # 獲取總頁數
    total_page = page_obj.pages
    resp_dict=dict(errno=RET.OK, errmsg="OK",data={"total_page":total_page})
    resp_json = json.dumps(resp_dict)
    # 設置緩存數據
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id,sort_key)
    # hash類型    
    try:
        redis_store.hset(redis_key, page , resp_json)
        redis_store.expire(redis_key,3600)
    except Exception as e:
        current_app.logger.erroe(e)
    return resp_json, 200, {"Content-Type":"application/json"}



