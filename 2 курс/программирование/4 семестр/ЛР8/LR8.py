from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import sessionmaker
import datetime

# было взято ORM - sqlalchemy 2.0
Base = declarative_base()

class Counter(Base):
    __tablename__ = 'counter'
    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    created = Column(DateTime)


engine = create_engine('sqlite:///data.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()


Base.metadata.create_all(engine)


def create_counter(id, value, created):
    new_counter = Counter(id=id, value=value, created=created)
    session.add(new_counter)
    session.commit()

def read_counters():
    counters = session.query(Counter).all()
    for counter in counters:
        print(counter.id, counter.value, counter.created)

def update_counter(id, new_value):
    counter = session.query(Counter).filter(Counter.id == id).first()
    counter.value = new_value
    session.commit()

def delete_counter(id):
    counter = session.query(Counter).filter(Counter.id == id).first()
    session.delete(counter)
    session.commit()

create_counter(1, 10, datetime.datetime.now())
read_counters()
update_counter(1, 20)
delete_counter(1)