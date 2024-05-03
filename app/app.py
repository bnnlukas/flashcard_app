from flask import Flask, render_template, request, Response, send_file
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import logging
import random
from io import TextIOWrapper
import csv
import pandas as pd

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres_db:5432/esp'
db = SQLAlchemy(app)

class EspGer(db.Model):
    __tablename__ = 'espger'
    spanish = db.Column(db.String(50), primary_key=True)
    german = db.Column(db.String(50))
    details = db.Column(db.String(50))
    rank = db.Column(db.Integer)

@app.route('/')
def home():
    try:
        weights = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

        ranks_from_table = db.session.query(EspGer.rank).all()
        try:
            records_from_table = db.session.query(EspGer.spanish, EspGer.german, EspGer.rank).all()
        except:
            records_from_table = db.session.query(EspGer.spanish, EspGer.german, EspGer.rank, EspGer.details).all()
        ranks = [rank[0] for rank in ranks_from_table]
        weights_for_ranks = [weights[rank] for rank in ranks]

        flashcard = random.choices(records_from_table, weights=weights_for_ranks, k=1)[0]
        
        return render_template('home.html', flashcard=flashcard)
    except:
        rows = EspGer.query.all()
        indexed_rows = [(index + 1, row) for index, row in enumerate(rows)]
        return render_template('admin.html', rows=indexed_rows)


@app.route('/admin')
def admin():
    rows = EspGer.query.all()
    indexed_rows = [(index + 1, row) for index, row in enumerate(rows)]
    return render_template('admin.html', rows=indexed_rows)

@app.route('/good_known', methods=['POST'])
def good():
    spanish_word = request.form['spanish_word']
    word_obj = EspGer.query.filter_by(spanish=spanish_word).first()
    if word_obj:
        if word_obj.rank < 5:
            word_obj.rank += 1
            logging.info(word_obj.rank)
            db.session.commit()
    return '', 204

@app.route('/ok_known', methods=['POST'])
def ok():
    return '', 204

@app.route('/bad_known', methods=['POST'])
def bad():
    spanish_word = request.form['spanish_word']
    word_obj = EspGer.query.filter_by(spanish=spanish_word).first()
    if word_obj:
        if word_obj.rank > 0:
            word_obj.rank -= 1
            logging.info(word_obj.rank)
            db.session.commit()
    return '', 204

@app.route('/admin/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        df = pd.read_csv(file, sep=';')
        existing_values = set(EspGer.query.with_entities(EspGer.spanish).all())
        existing_values_list = [item[0] for item in existing_values]
        new_values = df['spanish'].drop_duplicates()
        new_values = new_values[~new_values.isin(existing_values_list)]
        new_data = df[df['spanish'].isin(new_values)]
        if 'rank' in new_data.columns:
            pass
        else:
            new_data['rank'] = 0
        new_data.to_sql(EspGer.__tablename__, db.engine, if_exists='append', index=False)
    return '', 204

@app.route('/delete_data_from_table', methods=['POST'])
def delete_data_from_table():
    try:
        db.session.query(EspGer).delete()
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return 'An error occurred while deleting data: ' + str(e)
    
@app.route('/admin/export_table', methods=['POST'])
def export_table():
    data = EspGer.query.all()
    df = pd.DataFrame([(row.spanish, row.german, row.rank) for row in data], columns=['spanish', 'german', 'rank'])  
    csv_data = df.to_csv(index=False, sep=';')

    return Response(
        csv_data,
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=data.csv'}
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)