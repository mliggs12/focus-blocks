from random import choice
from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///focusblocks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class FocusBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heading = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    statements = db.relationship('Statement', backref='focusblock', lazy=True)

    def __repr__(self):
        return f'<FocusBlock {self.id}>'
    
class Statement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=True)
    position = db.Column(db.Integer, nullable=False)
    focusblock_id = db.Column(db.Integer, db.ForeignKey('focus_block.id'), nullable=False)

    def __repr__(self):
        return f'<Statement {self.id} - FocusBlock {self.focusblock_id}>'

class FocusBlockForm(FlaskForm):
    heading = StringField('What is bothering me?', validators=[DataRequired()])
    submit = SubmitField('Create')

@app.route('/')
def index():
    focusblocks = FocusBlock.query.filter_by(completed=False).all()

    return render_template('index.html', focusblocks=focusblocks)

@app.route('/create', methods=['GET', 'POST'])
def create():
    form = FocusBlockForm()
    if form.validate_on_submit():
        heading = form.heading.data
        focusblock = FocusBlock(heading=heading)
        db.session.add(focusblock)
        db.session.commit()
        flash('FocusBlock created successfully!')

        return redirect(url_for('focusblock', focusblock_id=focusblock.id))
    
    return render_template('create.html', form=form)

@app.route('/focusblock/<int:focusblock_id>', methods=['GET', 'POST'])
def focusblock(focusblock_id):
    focusblock = FocusBlock.query.get_or_404(focusblock_id)
    if request.method == 'POST':
        for i in range(1, 13):
            statement = Statement.query.filter_by(focusblock_id=focusblock.id, position=i).first()
            statement_text = request.form.get(f'statement-{i}', '').strip()
            
            if statement_text and not statement:
                new_statement = Statement(text=statement_text, position=i, focusblock_id=focusblock.id)
                db.session.add(new_statement)
        
        focusblock.completed = 'completed' in request.form
        db.session.commit()
        flash('FocusBlock updated successfully!')

        return redirect(url_for('index'))

    return render_template('focusblock.html', focusblock=focusblock)


@app.route('/random')
def random():
    focusblocks = FocusBlock.query.filter_by(completed=False).all()
    if focusblocks:
        focusblock = choice(focusblocks)

        return redirect(url_for('focusblock', focusblock_id=focusblock.id))
    
    else:
        flash('No incomplete FBs found')

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
