import random
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session
import os
from app import models, schemas, database, auth
from pathlib import Path
import shutil
from pydub import AudioSegment

from app.outside_logic.audio_logic import analyze_audio_volume_and_pauses, TextComparer, recognize

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

read_list = [
    "Природа – это бескрайний источник вдохновения. Леса, поля, реки и горы дарят человеку покой и гармонию. Прогулка по утреннему лесу наполняет душу свежестью, а пение птиц создает неповторимую мелодию. Каждая травинка, каждый листок – часть огромного живого организма. В природе нет ничего лишнего, все взаимосвязано. Человек должен бережно относиться к этому богатству, чтобы сохранить его для будущих поколений.",
    "Весной природа пробуждается от зимнего сна. Первые лучи солнца прогревают землю, и из-под снега пробиваются нежные ростки. Деревья покрываются молодыми листьями, а в воздухе разливается аромат цветущих растений. Реки освобождаются ото льда, и их журчание наполняет мир музыкой. Весна – это время обновления, когда все вокруг дышит жизнью и радостью.",
    "Лето – это буйство красок и тепла. Солнце дарит свою энергию всему живому, наполняя природу яркими красками. Луга утопают в разнотравье, а леса становятся густыми и зелеными. В воздухе кружат бабочки, а пчелы трудятся над сбором нектара. Летние дожди освежают землю, а после них воздух наполняется ароматом свежести. Это время изобилия и радости.",
    "Осень – пора увядания и тихой красоты. Листья деревьев окрашиваются в золотые, багряные и коричневые тона. Лес становится похож на волшебную сказку. Воздух наполнен прохладой, а по утрам трава покрывается серебристой росой. Птицы собираются в стаи, готовясь к перелету. Осень – это время размышлений и спокойствия, когда природа готовится к зимнему отдыху.",
    "Зима превращает мир в белоснежное царство. Деревья одеваются в пушистые снежные шапки, а земля укрывается мягким ковром. Морозный воздух бодрит и освежает. В тишине зимнего леса слышен только скрип снега под ногами. Реки и озера замерзают, превращаясь в зеркальные поверхности. Зима – это время покоя и умиротворения, когда природа отдыхает перед новым циклом жизни.",
    "Горы – это величественные исполины, устремленные в небо. Их склоны покрыты лесами, а вершины скрыты облаками. Горный воздух чист и прозрачен, а виды завораживают своей красотой. В горах время течет иначе, и человек чувствует себя частью чего-то большего. Альпийские луга, бурные реки и тихие озера делают горы местом силы и вдохновения.",
    "Океан – это бескрайняя стихия, полная тайн и загадок. Его волны то ласково шепчут, то грозно ревут. Вода переливается всеми оттенками синего, а на горизонте сливается с небом. Океан дарит жизнь миллионам существ, от крошечных планктонов до гигантских китов. Шум прибоя успокаивает душу, а морской бриз наполняет энергией.",
    "Лес – это легкие нашей планеты. Деревья очищают воздух, дают приют животным и дарят людям прохладу. В густой чаще царит особый микроклимат, где каждый звук имеет значение. Лес полон загадок: то тут, то там мелькнет белка, раздастся стук дятла или шелест листьев под лапой лисы. Это место, где можно ощутить единение с природой.",
    "Река – это вечное движение. Она берет начало где-то в горах и несет свои воды к океану. По пути она дает жизнь растениям и животным, формируя уникальные экосистемы. Течение реки может быть бурным и стремительным или плавным и спокойным. Вода в ней постоянно меняется, но река всегда остается собой – символом жизни и постоянства.",
    "Пустыня – это царство песка и солнца. Днем здесь невыносимая жара, а ночью температура резко падает. Кажется, что в пустыне нет жизни, но это не так. Кактусы, ящерицы, змеи и другие существа приспособились к суровым условиям. Пустыня учит нас выживанию и показывает, насколько хрупок баланс между жизнью и стихией."
]

repeat_list = [
    "Лес полон жизни. Птицы поют в кронах деревьев, белки прыгают с ветки на ветку, а под ногами шуршат опавшие листья. Воздух наполнен ароматом хвои и свежести. Здесь царит гармония.",
    "Река несет свои воды через долины и горы. Ее течение то спокойное, то бурное. На берегах растут ивы, а в воде плещется рыба. Река – это вечное движение.",
    "Горы величественны и неприступны. Их вершины теряются в облаках, а склоны покрыты лесами. В горах тишина, нарушаемая лишь шумом ветра и криками орлов.",
    "Луга летом утопают в цветах. Ромашки, васильки и клевер создают пестрый ковер. Над ними кружат пчелы и бабочки. Здесь царит покой и солнечное тепло.",
    "Океан бескрайний и загадочный. Его волны то ласковые, то грозные. Вода переливается всеми оттенками синего. Океан дарит ощущение свободы и вечности.",
    "Осенью лес меняет наряд. Листья становятся золотыми, красными, оранжевыми. Воздух прохладен, а под ногами шуршит ковер из листвы. Это время тихой красоты.",
    "Пустыня кажется безжизненной, но это не так. Кактусы, ящерицы и змеи приспособились к жаре. Ночью здесь холодно, а днем – палящее солнце. Суровая, но прекрасная земля.",
    "Весной природа пробуждается. Почки набухают, появляются первые цветы, а птицы возвращаются с юга. Воздух наполнен ароматами свежести. Это время обновления.",
    "Зимой лес засыпает. Деревья укрыты снегом, а земля – белым покрывалом. Тишину нарушает лишь скрип снега под ногами. Морозный воздух бодрит и очищает.",
    "Болото – мир тишины и спокойствия. Здесь растут клюква и осока, а в воде прячутся лягушки. Болота – важная часть экосистемы, фильтрующая воду и дающая приют многим видам."
]

@router.get("/text-for-auditions", response_model=schemas.TextAuditionResponse)
def get_texts_for_auditions():
    # Выбираем случайный элемент из каждого списка
    read_index = random.randint(0, len(read_list) - 1)
    repeat_index = random.randint(0, len(repeat_list) - 1)

    # Отправляем их в ответ
    return schemas.TextAuditionResponse(
        read_text=read_list[read_index],
        repeat_text=repeat_list[repeat_index],
        read_index=read_index,
        repeat_index=repeat_index,
    )

@router.post("/text-audition-result")
async def post_text_audition_result(
    read_text_index: int = Form(...),
    repeat_text_index: int = Form(...),
    read_text_file: UploadFile = File(...),
    repeat_text_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    try:
        upload_folder = "uploads/audio_files"
        Path(upload_folder).mkdir(parents=True, exist_ok=True)

        # Сохранение первого файла
        read_text_file_path = os.path.join(upload_folder, read_text_file.filename)
        with open(read_text_file_path, "wb") as buffer:
            shutil.copyfileobj(read_text_file.file, buffer)

        # Сохранение второго файла
        repeat_text_file_path = os.path.join(upload_folder, repeat_text_file.filename)
        with open(repeat_text_file_path, "wb") as buffer:
            shutil.copyfileobj(repeat_text_file.file, buffer)

        with open('logs.txt', 'a') as file:
            file.write(f"hoy {read_text_file_path} \n")
        with open('logs.txt', 'a') as file:
            file.write(f"hoy {repeat_text_file_path} \n")

        wav_filename = os.path.splitext(read_text_file.filename)[0] + ".wav"
        read_text_file_converted_path = os.path.join(upload_folder, wav_filename)
        audio = AudioSegment.from_file(read_text_file_path, format="m4a")
        audio.export(read_text_file_converted_path, format="wav")

        wav_filename = os.path.splitext(repeat_text_file.filename)[0] + ".wav"
        repeat_text_file_converted_path = os.path.join(upload_folder, wav_filename)
        audio = AudioSegment.from_file(repeat_text_file_path, format="m4a")
        audio.export(repeat_text_file_converted_path, format="wav")

        with open('logs.txt', 'a') as file:
            file.write(f"hoy {read_text_file_converted_path} \n")
        with open('logs.txt', 'a') as file:
            file.write(f"hoy {repeat_text_file_converted_path} \n")

        transcript_read = recognize(read_text_file_converted_path)
        with open('logs.txt', 'a') as file:
            file.write(f"hoy {transcript_read} \n")
        transcript_repeat = recognize(repeat_text_file_converted_path)
        with open('logs.txt', 'a') as file:
            file.write(f"hoy {transcript_repeat} \n")
        comparer = TextComparer(language='russian')
        read_analysis = comparer.analyze(read_list[read_text_index], transcript_read)
        repeat_analysis = comparer.analyze(repeat_list[repeat_text_index], transcript_repeat)
        quality_score_read = float(read_analysis['scores']['overall_score']/100)
        quality_score_repeat = float(repeat_analysis['scores']['overall_score']/100)
        average_volume_read, pauses_count_read = analyze_audio_volume_and_pauses(read_text_file_converted_path)
        average_volume_repeat, pauses_count_repeat = analyze_audio_volume_and_pauses(repeat_text_file_converted_path)


        #with open('logs.txt', 'a') as  file:
         #   file.write(f"db {quality_score_read} {quality_score_repeat} {average_volume_read} {pauses_count_read} {average_volume_repeat} {pauses_count_repeat} \n")
        #with open('logs.txt', 'a') as  file:
         #   file.write(f"db {transcript_read} \n")
        #with open('logs.txt', 'a') as file:
          #  file.write(f"db {transcript_repeat} \n")
       # with open('logs.txt', 'a') as file:
           # file.write(f"db {read_analysis} \n")
        #with open('logs.txt', 'a') as file:
            #file.write(f"db {repeat_analysis} \n")
        # Сохраняем информацию в базе данных
        text_audition_result = models.TextAuditionResults(
            user_id=user.id,
            read_text_path=read_text_file_path,
            repeat_text_path=repeat_text_file_path,
            quality_score_read=quality_score_read,
            quality_score_repeat=quality_score_repeat,
            pauses_count_read=float(pauses_count_read),
            pauses_count_repeat=float(pauses_count_repeat),
            average_volume_read=float(average_volume_read),
            average_volume_repeat=float(average_volume_repeat)
        )
        db.add(text_audition_result)
        db.commit()
        db.refresh(text_audition_result)

        return {"status": "added"}
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))