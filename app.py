import os

from flask import Flask, render_template, request, session, redirect
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, validators

app = Flask(__name__)


# pulling config settings
app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

# starting db
db = SQLAlchemy(app)

# setting up OIDC
auth = OIDCAuthentication(app, issuer=app.config["OIDC_ISSUER"],
                          client_registration_info=app.config["OIDC_CLIENT_CONFIG"])

class Skills(db.Model):
     user = db.Column(db.String(50), primary_key=True)
     skill = db.Column(db.String(50), primary_key=True)
     level = db.Column(db.String(50))


@app.route('/')
@auth.oidc_auth
def index():
    return render_template('home.html')

@app.route('/logout')
#@auth.oidc_logout
def logout():
    return render_template('logout.html')

@app.route('/about')
@auth.oidc_auth
def about():
    return render_template('about.html')

@app.route('/skills')
@auth.oidc_auth
def skills():
    uid = str(session["userinfo"].get("preferred_username", ""))
    data = Skills.query.filter_by(user=uid).all()
    return render_template('skills.html', data=data)

@app.route('/addskills', methods=['POST'])
@auth.oidc_auth
def addskills():
    uid = str(session["userinfo"].get("preferred_username", ""))
    newskill = request.form.get('newSkill')
    level = request.form['level']

    if Skills.query.filter_by(user=uid, skill=newskill).first() is not None:
        skill = Skills.query.filter_by(user=uid, skill=newskill).first()
        skill.level = level
        db.session.commit()
    elif Skills.query.filter_by(skill=newskill).first() is None:
        yourLevel = Skills(user=uid, skill=newskill, level=level)
        db.session.add(yourLevel)
        db.session.commit()

    data = Skills.query.filter_by(user=uid).all()

    return redirect('/skills')


if __name__ == '__main__':
    app.run(debug=True)
