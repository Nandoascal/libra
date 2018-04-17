import os

from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# pulling config settings
if os.path.exists(os.path.join(os.getcwd(), "config.env.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))

# starting db
db = SQLAlchemy(app)

# setting up OIDC
auth = OIDCAuthentication(app, issuer=app.config["OIDC_ISSUER"],
                          client_registration_info=app.config["OIDC_CLIENT_CONFIG"])

class Skills(db.Model):
     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     user = db.Column(db.String(50), primary_key=True)
     skill = db.Column(db.String(50), primary_key=True)
     level = db.Column(db.String(50))


@app.route('/')
@app.route('/skills')
@auth.oidc_auth
def skills():
    uid = str(session["userinfo"].get("preferred_username", ""))
    data = Skills.query.filter_by(user=uid).all()
    return render_template('skills.html', data=data, user=uid)

@app.route('/skills/', methods=['POST'])
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

    return redirect('/')

@app.route('/skills/<user>')
@auth.oidc_auth
def userSkill(user):
    uid = str(session["userinfo"].get("preferred_username", ""))
    if user == uid:
        return redirect('/skills')
    else:
        data = Skills.query.filter_by(user=user).all()
        return render_template('otherUserSkills.html', data=data, user=user)

@app.route('/edit/<user>/<id>')
@auth.oidc_auth
def edit(user, id):
    skill = Skills.query.filter_by(id=id, user=user).first()
    return render_template('edit.html', user=user, id=id, skill=skill)

@app.route('/edit/<user>/<id>/', methods=['POST'])
@auth.oidc_auth
def editSkill(user, id):
    newLevel = request.form['level']
    oldSkill = Skills.query.filter_by(user=user, id=id).first()
    oldSkill.level = newLevel
    db.session.commit()
    return redirect('/')

@app.route('/delete/<user>/<id>')
@auth.oidc_auth
def delete(user, id):
    rip = Skills.query.filter_by(id=id, user=user).first()
    db.session.delete(rip)
    db.session.commit()
    return redirect('/')

@app.route('/users')
@auth.oidc_auth
def users():
    data = db.session.query(Skills.user).distinct()
    return render_template('users.html', data=data, location=request.path)

@app.route('/search', methods=['POST'])
@auth.oidc_auth
def search():
    searchTarget = request.form['searchTarget']
    results = Skills.query.filter(Skills.skill.like("%" + searchTarget + "%")).all()
    if not results:
        return render_template('searchResults.html', results=None)
    else:
        return render_template('searchResults.html', results=results)


@app.route('/logout')
@auth.oidc_logout
def logout():
    return 'You\'ve been successfully logged out!'

if __name__ == '__main__':
    app.run(host=app.config['IP'], port=app.config['PORT'])
