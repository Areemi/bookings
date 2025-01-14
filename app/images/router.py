from fastapi import APIRouter, UploadFile
import shutil

from app.tasks.tasks import process_picture


router = APIRouter(
    prefix="/images",
    tags=["Download images"]
)

@router.post("/hotels")
async def add_hotel_image(name: int, file: UploadFile):
    im_path = f"app/static/images/{name}.webp"
    with open(im_path, "wb+") as file_object:
        # Сохраняем файл в локальное хранилище (на практике обычно сохраняется в удаленное хранилище)
        shutil.copyfileobj(file.file, file_object)
        # Отдаем Celery фоновую задачу на обработку картинки
        process_picture.delay(im_path)