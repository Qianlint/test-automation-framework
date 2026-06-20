from sqlalchemy import create_engine, Column, Integer, String, Double, ForeignKey, TIMESTAMP
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func

engine = create_engine("mysql+pymysql://root:test1234@127.0.0.1:3306/autotest")
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Testcase(Base):
    __tablename__ = 'testcase'

    id = Column(Integer, primary_key=True, autoincrement=True)
    library = Column(String(50))
    problem = Column(String(50))
    solver = Column(String(50))

    samples = relationship('BenchmarkSample', back_populates='testcase')


class BenchmarkSample(Base):
    __tablename__ = 'benchmark_sample'

    id = Column(Integer, primary_key=True, autoincrement=True)
    benchmark_id = Column(String(36))
    testcase_id = Column(Integer, ForeignKey('testcase.id'))
    threads = Column(Integer)
    execution_time = Column(Double)
    step_size_tolerance = Column(Double)
    error = Column(Double)
    created_at = Column(TIMESTAMP, server_default=func.now())

    testcase = relationship('Testcase', back_populates='samples')