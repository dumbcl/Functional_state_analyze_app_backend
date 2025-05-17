from sqlalchemy.orm import Session
from models import RufieTestResult
from database import SessionLocal

def update_rufie_indexes():
    db: Session = SessionLocal()
    try:
        results = db.query(RufieTestResult).all()
        for r in results:
            new_index = RufieTestResult.calculate_rufie_index(
                r.measurement_first,
                r.measurement_second,
                r.measurement_third
            )
            r.rufie_index = new_index
            r.result_estimation = RufieTestResult.calculate_result_estimation(new_index)
        db.commit()
        print(f'Updated {len(results)} rows.')
    finally:
        db.close()


update_rufie_indexes()