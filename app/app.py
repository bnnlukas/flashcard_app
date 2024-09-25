from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import random
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres_db:5432/esp'
db = SQLAlchemy(app)

class EspGer(db.Model):
    __tablename__ = 'espger'
    spanish = db.Column(db.String(150), primary_key=True)
    german = db.Column(db.String(150))
    type = db.Column(db.String(100))
    details = db.Column(db.String(300))
    lastknown = db.Column(db.DateTime)
    rank = db.Column(db.Integer)

@app.route('/')
def home():
    try:
        current_time = datetime.utcnow()

        records_from_table = db.session.query(EspGer.spanish, EspGer.german, EspGer.type, EspGer.details, EspGer.lastknown, EspGer.rank).filter(
            db.and_(
                db.or_(
                    db.and_(EspGer.rank == 1),
                    db.and_(EspGer.rank == 2, EspGer.lastknown <= (current_time - timedelta(days=1))),
                    db.and_(EspGer.rank == 3, EspGer.lastknown <= (current_time - timedelta(days=3))),
                    db.and_(EspGer.rank == 4, EspGer.lastknown <= (current_time - timedelta(days=7))),
                    db.and_(EspGer.rank == 5, EspGer.lastknown <= (current_time - timedelta(days=21)))
                )
            )
        ).all()

        random.shuffle(records_from_table)
        flashcard = records_from_table[0]
        if flashcard.rank == 1:
            flashcard_dir = 0
        else:
            flashcard_dir = random.randint(0, 1)
        
        return render_template('home.html', flashcard=flashcard, flashcard_dir=flashcard_dir)
    except:
        try:    
            rows = EspGer.query.all()
            indexed_rows = [(index + 1, row) for index, row in enumerate(rows)]
            return render_template('admin.html', rows=indexed_rows)
        except:
            return render_template('admin.html')

@app.route('/admin')
def admin():
    try:    
        rows = EspGer.query.all()
        rank_counts = db.session.query(EspGer.rank, db.func.count()).group_by(EspGer.rank).all()
        rank_counts_json = [[rank, count] for rank, count in rank_counts]
        indexed_rows = [(index + 1, row) for index, row in enumerate(rows)]
        return render_template('admin.html', rows=indexed_rows, rank_counts_json=rank_counts_json)
    except:
        return render_template('admin.html')

@app.route('/good_known', methods=['POST'])
def good():
    spanish_word = request.form['spanish_word']
    word_obj = EspGer.query.filter_by(spanish=spanish_word).first()
    if word_obj:
        if word_obj.rank < 5:
            word_obj.rank += 1
            word_obj.lastknown = datetime.utcnow()
            db.session.commit()
    return '', 204

@app.route('/bad_known', methods=['POST'])
def bad():
    spanish_word = request.form['spanish_word']
    word_obj = EspGer.query.filter_by(spanish=spanish_word).first()
    if word_obj:
        if word_obj.rank > 1:
            word_obj.rank = 1
            db.session.commit()
    return '', 204

@app.route('/admin/upload_file', methods=['POST'])
def upload_file():
    sheets_names = ['verb', 'substantiv', 'weitere']
    file = request.files['file']
    if file:
        csv_file = pd.ExcelFile(file)
        dfs = {}
        for sheet_name in sheets_names:
            dfs[sheet_name] = pd.read_excel(csv_file, sheet_name)
            dfs[sheet_name]['type'] = sheet_name
        
        df = pd.concat(dfs.values(), ignore_index=True)
        
        existing_values = set(EspGer.query.with_entities(EspGer.spanish).all())
        existing_values_list = [item[0] for item in existing_values]
        new_values = df['spanish'].drop_duplicates()
        new_values = new_values[~new_values.isin(existing_values_list)]
        new_data = df[df['spanish'].isin(new_values)]
        if 'rank' in new_data.columns:
            pass
        else:
            new_data['rank'] = 1
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
    df = pd.DataFrame([(row.spanish, row.german, row.type, row.details, row.rank) for row in data], columns=['spanish', 'german', 'type', 'details', 'rank'])  
    
    # Create a BytesIO object to store the Excel file
    excel_file = BytesIO()

    # Create a Pandas Excel writer using the BytesIO object
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        # Loop through each unique type and write the corresponding data to a separate sheet
        for type_name, group_df in df.groupby('type'):
            group_df.to_excel(writer, sheet_name=type_name, index=False)

    # Reset the BytesIO object position to the beginning
    excel_file.seek(0)

    # Return the Excel file as a Flask response
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='data.xlsx'
    )

@app.route('/create_table', methods=['POST'])
def create_table():
    db.create_all()
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)