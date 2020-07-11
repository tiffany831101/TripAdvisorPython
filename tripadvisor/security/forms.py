from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_admin.form.widgets import DatePickerWidget
from flask import current_app, flash

from wtforms import StringField, PasswordField, BooleanField, \
                    SubmitField, DateField, SelectField, TextField
from wtforms.validators import DataRequired, Length, Email, \
                                Regexp, EqualTo, InputRequired
from wtforms import ValidationError

from tripadvisor.models import User
from tripadvisor import photos


    

class UserInfomationForm(Form):
    gender = SelectField(u"性別", choices=[("男","男"),("女","女")],validators=[DataRequired()])
    birthday = DateField(u'生日,例如2000/12/11',format='%Y-%m-%d',validators=[DataRequired(u'請務必輸入正確格式')], widget=DatePickerWidget())
    user_id=StringField(u'身分證字號',validators=[DataRequired(),Regexp("^[A-Z][0-9]{9}",message=u"無效的身分證號碼，請再次確認")])
    country = SelectField(u"縣市區域", choices=[("台北","台北市"),("新北","新北市"),("宜蘭","宜蘭縣"),("桃園","桃園市"),
            ("苗栗","苗栗縣"),("台中","台中市"),("彰化","彰化縣"),("雲林","雲林縣"),("嘉義","嘉義縣"),("台南","台南市"),("高雄","高雄市"),
            ("屏東","屏東縣"),("宜蘭","宜蘭縣"),("花蓮","花蓮縣"),("台東","台東縣")],validators=[DataRequired(u'請務必輸入正確格式')])
    address = TextField(u"常用地址",validators=[DataRequired(u'請務必輸入正確格式')])
    LINE = StringField(u"LINE ID",validators=[DataRequired(u'請務必輸入正確格式')])
    submit= SubmitField('提交')
    def valiadate_user_id(self, field):
        if User.query.filter_by(user_id=field.data).first():
            flash(u'該身分證字號已被註冊')
            raise ValidationError(u'該身分證字號已被註冊')

class UploadImageForm(Form):
    photo = FileField(validators=[
                        FileAllowed(photos, '只能上傳圖片'),
                        FileRequired('沒有選擇文件')]
                    )
    submit = SubmitField('上傳')
