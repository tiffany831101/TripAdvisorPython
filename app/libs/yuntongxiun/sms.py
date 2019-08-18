#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser

#主帳號
accountSid= "8a216da86bfdbeb5016c13323ef80b56"

#主帳號Token
accountToken= '43296b7286af4e928ade1cbf2f59c850'

#應用Id
appId='8a216da86bfdbeb5016c13323f6b0b5d'

#請求地址，格式如下，不需要寫https://
serverIP='app.cloopen.com'

#請求端口
serverPort='8883'

#REST版本號
softVersion='2013-12-26'

  # 發送模板短信
  # @param to 手機號
  # @param datas 內容數據 格式為列表  ''
  # @param $tempId 模板Id


class CCP(object):
  """自己封裝的發送短信的輔助類"""
  # 用來保存對象的類屬性
  instance=None
  
  def __new__(cls):
  # 判斷CCP類有沒有已經創建好的對象，如果沒有，創建一個對象，並且保存
    # 如果有，則將保存的對象直接返回
    if cls.instance is None:
      obj = super(CCP, cls).__new__(cls)
      
      #初始化RESET_SDK
      obj.rest = REST(serverIP,serverPort,softVersion)
      obj.rest.setAccount(accountSid,accountToken)
      obj.rest.setAppId(appId)
      
      cls.instance = obj
      
      return cls.instance


  def send_trmplates_sms(self,todatas,temp_id):
    result = rest.sendTemplateSMS(to,datas,tempId)
    # for k,v in result.iteritems(): 
        
    #     if k=='templateSMS' :
    #             for k,s in v.iteritems(): 
    #                 print '%s:%s' % (k, s)
    #     else:
    #         print '%s:%s' % (k, v)
    status_code = result.get("statusCode")
    if status_code =="000000":
      #表示發送成功
      return 0 
    else:
      # 表示發送失敗
      return -1
if __name__=="__main__":
  ccp=CCP()
  ret = ccp.send_trmplates_sms("18811071718",["1234","5"], 1)
  print(ret)
#sendTemplateSMS(手機號碼,內容數據,模板Id)