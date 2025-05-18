import pandas as pd
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from datetime import date

from database import SessionLocal
from models import ShtangeTestResult, RufieTestResult, StrupTestResult, GenchTestResult, ReactionsTestResult, \
    TextAuditionResults, PersonalReportTestResult


# Фильтры
user_ids = [5, 6, 7, 8, 10, 14, 15, 16, 17, 18, 19]
start_date = date(2025, 5, 13)

def fetch_data(session):
    # Извлечение данных из ShtangeTestResult
    shtange_query = session.query(
        ShtangeTestResult.user_id,
        ShtangeTestResult.breath_hold_seconds.label('shtange_breath_hold_seconds'),
        ShtangeTestResult.reaction_indicator.label('shtange_reaction_indicator'),
        ShtangeTestResult.test_date
    ).filter(ShtangeTestResult.user_id.in_(user_ids), ShtangeTestResult.test_date >= start_date).all()

    # Извлечение данных из RufieTestResult
    rufie_query = session.query(
        RufieTestResult.user_id,
        RufieTestResult.rufie_index.label('rufie_index'),
        RufieTestResult.test_date
    ).filter(RufieTestResult.user_id.in_(user_ids), RufieTestResult.test_date >= start_date).all()

    # Извлечение данных из StrupTestResult
    strup_query = session.query(
        StrupTestResult.user_id,
        StrupTestResult.result.label('strup_result'),
        StrupTestResult.test_date
    ).filter(StrupTestResult.user_id.in_(user_ids), StrupTestResult.test_date >= start_date).all()

    # Извлечение данных из GenchTestResult
    gench_query = session.query(
        GenchTestResult.user_id,
        GenchTestResult.breath_hold_seconds.label('gench_breath_hold_seconds'),
        GenchTestResult.reaction_indicator.label('gench_reaction_indicator'),
        GenchTestResult.test_date
    ).filter(GenchTestResult.user_id.in_(user_ids), GenchTestResult.test_date >= start_date).all()

    # Извлечение данных из ReactionsTestResult
    reactions_query = session.query(
        ReactionsTestResult.user_id,
        ReactionsTestResult.visual_average_diff.label('visual_average_diff'),
        ReactionsTestResult.audio_average_diff.label('audio_average_diff'),
        ReactionsTestResult.visual_quav_diff.label('visual_quav_diff'),
        ReactionsTestResult.audio_quav_diff.label('audio_quav_diff'),
        ReactionsTestResult.visual_errors.label('visual_errors'),
        ReactionsTestResult.audio_errors.label('audio_errors'),
        ReactionsTestResult.test_date
    ).filter(ReactionsTestResult.user_id.in_(user_ids), ReactionsTestResult.test_date >= start_date).all()

    # Извлечение данных из TextAuditionResults
    text_audition_query = session.query(
        TextAuditionResults.user_id,
        TextAuditionResults.quality_score_read.label('quality_score_read'),
        TextAuditionResults.quality_score_repeat.label('quality_score_repeat'),
        TextAuditionResults.pauses_count_read.label('pauses_count_read'),
        TextAuditionResults.pauses_count_repeat.label('pauses_count_repeat'),
        TextAuditionResults.test_date
    ).filter(TextAuditionResults.user_id.in_(user_ids), TextAuditionResults.test_date >= start_date).all()

    # Извлечение данных из PersonalReportTestResult
    personal_report_query = session.query(
        PersonalReportTestResult.user_id,
        PersonalReportTestResult.performance_measure.label('performance_measure'),
        PersonalReportTestResult.test_date
    ).filter(PersonalReportTestResult.user_id.in_(user_ids), PersonalReportTestResult.test_date >= start_date).all()

    shtange_df = pd.DataFrame(shtange_query,
                              columns=['user_id', 'shtange_breath_hold_seconds', 'shtange_reaction_indicator',
                                       'test_date'])
    rufie_df = pd.DataFrame(rufie_query, columns=['user_id', 'rufie_index', 'test_date'])
    strup_df = pd.DataFrame(strup_query, columns=['user_id', 'strup_result', 'test_date'])
    gench_df = pd.DataFrame(gench_query,
                            columns=['user_id', 'gench_breath_hold_seconds', 'gench_reaction_indicator', 'test_date'])
    reactions_df = pd.DataFrame(reactions_query,
                                columns=['user_id', 'visual_average_diff', 'audio_average_diff', 'visual_quav_diff',
                                         'audio_quav_diff', 'visual_errors', 'audio_errors', 'test_date'])
    text_audition_df = pd.DataFrame(text_audition_query,
                                    columns=['user_id', 'quality_score_read', 'quality_score_repeat',
                                             'pauses_count_read', 'pauses_count_repeat', 'test_date'])
    personal_report_df = pd.DataFrame(personal_report_query, columns=['user_id', 'performance_measure', 'test_date'])

    # Возвращаем все данные в виде DataFrame
    return shtange_df, rufie_df, strup_df, gench_df, reactions_df, text_audition_df, personal_report_df


def merge_data(shtange_df, rufie_df, strup_df, gench_df, reactions_df, text_audition_df, personal_report_df):
    # Объединение всех DataFrame по user_id и test_date
    merged_df = shtange_df.merge(rufie_df, on=['user_id', 'test_date'], how='outer')
    merged_df = merged_df.merge(strup_df, on=['user_id', 'test_date'], how='outer')
    merged_df = merged_df.merge(gench_df, on=['user_id', 'test_date'], how='outer')
    merged_df = merged_df.merge(reactions_df, on=['user_id', 'test_date'], how='outer')
    merged_df = merged_df.merge(text_audition_df, on=['user_id', 'test_date'], how='outer')
    merged_df = merged_df.merge(personal_report_df, on=['user_id', 'test_date'], how='outer')

    return merged_df


# Получаем все данные
db: Session = SessionLocal()
shtange_df, rufie_df, strup_df, gench_df, reactions_df, text_audition_df, personal_report_df = fetch_data(db)

# Объединяем данные
final_df = merge_data(shtange_df, rufie_df, strup_df, gench_df, reactions_df, text_audition_df, personal_report_df)

# Сохраняем итоговый DataFrame в CSV
final_df.to_csv('merged_data.csv', index=False)
db.close()