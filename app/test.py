from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random

# Creating SQLAlchemy engine
engine = create_engine('postgresql://postgres:postgres@postgres_db:5432/esp')
Base = declarative_base()

class EspGer(Base):
    __tablename__ = 'espger'
    spanish = Column(Text, primary_key=True)
    german = Column(Text)
    rank = Column(Integer)

# Creating table if not exists
Base.metadata.create_all(engine)

# Creating session
Session = sessionmaker(bind=engine)
session = Session()

# Function to select a record with desired probability distribution
def select_record():

    weights = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

    ranks_from_table = session.query(EspGer.rank).all()
    records_from_table = session.query(EspGer.spanish, EspGer.german, EspGer.rank).all()
    print(records_from_table)
    ranks = [rank[0] for rank in ranks_from_table]
    print(ranks)
    weights_for_ranks = [weights[rank] for rank in ranks]
    print(weights_for_ranks)

    # Select a random index based on weights
    flashcard = random.choices(records_from_table, weights=weights_for_ranks, k=1)[0]
    print(index)
    print(records_from_table[index])

    return records_from_table[index]

# Example usage
selected_record = select_record()
print(selected_record.text, selected_record.rank)