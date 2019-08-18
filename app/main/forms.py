from flask_wtf import Form
from wtforms import StringField, SubmitField, IntegerField, FloatField, DateField, SelectMultipleField, SelectField, PasswordField, TextAreaField
from wtforms.validators import DataRequired,InputRequired,Length,Optional,Regexp, Email

class QueryForm(Form):
    date = DateField(u'用餐時間',format='%Y-%m-%d',validators=[DataRequired(u'請務必輸入正確格式')])
    price = IntegerField(u"消費金額",validators=[InputRequired()])
    satisfication = SelectField(u"消費餐點滿意度",choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')],validators=[DataRequired()])
    feedback = TextAreaField(u"意見內容")
    needreply =  SelectField(u"意見回饋",choices=[('需要','需要'),('不需要','不需要')])
    intention = SelectField(u"是否願意再來老漁村消費",choices=[('是','是'),('否','否')])
    food = SelectMultipleField(u"推薦的料理",choices=[('1','白斬雞'),('2','貴妃油雞'),('3','竹筍沙拉'),('4','竹筍香菇雞湯'),
    ('5','清蒸石斑魚'),('6','孔雀蛤'),('7','金沙軟絲'),('8','金沙杏胞菇'),('9','生魚片'),('10','番茄牛肉'),
    ('11','宮保雞丁'),('12','空心菜羊肉'),('13','肉絲炒飯')])
    submit = SubmitField(u'提交')




class EditionProfileForm(Form):
    name = StringField('論壇暱稱', validators=[Length(0,64)])
    location = StringField('所居地址', validators=[Length(0,64)])
    about_me = TextAreaField('自我介紹')
    submit= SubmitField('提交')

class PostForm(Form):
    body = TextAreaField('發表食記', validators=[DataRequired()])
    submit = SubmitField('提交')

class BookingForm(Form):
    people= IntegerField("人數", validators=[DataRequired()])
    booking_date =  DateField(u'日期',format='%Y-%m-%d',validators=[DataRequired()])
    booking_time = SelectField(u'餐次',choices=[('午餐','午餐'),('晚餐','晚餐')],validators=[DataRequired()])
    submit = SubmitField('提交')