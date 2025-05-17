import json
from sqlalchemy.orm import Session
from app.models import RufieTestResult, ReactionsTestResult
from app.database import SessionLocal

def add_reaction_avg():
    db: Session = SessionLocal()
    try:
        results = db.query(ReactionsTestResult).all()
        for r in results:

            av_diff, quav_diff = ReactionsTestResult.mean_std_difference([tuple(x) for x in json.loads(r.audio)])
            r.audio_average_diff = av_diff
            r.audio_quav_diff = quav_diff

            av_diff, quav_diff = ReactionsTestResult.mean_std_difference([tuple(x) for x in json.loads(r.visual)])
            r.visual_average_diff = av_diff
            r.visual_quav_diff = quav_diff
        db.commit()
        print(f'Updated {len(results)} rows.')
    finally:
        db.close()


add_reaction_avg()