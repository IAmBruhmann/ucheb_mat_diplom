# Учебные материалы

Новый проект по мотивам приложения с каталогом товаров, но предметная область заменена на учебные материалы.

## Что нужно для запуска

- Windows;
- Python **3.12** (рекомендуется для VS Code);
- VS Code с расширением **Python** (Pylance);
- доступ к терминалу PowerShell.

## Структура проекта

- `learning_materials/main.py` — точка входа
- `learning_materials/database.py` — работа с SQLite
- `learning_materials/constants.py` — пути и цвета интерфейса
- `learning_materials/ui/` — экраны и диалоги PyQt6

## Возможности

- вход по ролям: студент, преподаватель, администратор;
- гостевой просмотр каталога;
- каталог учебных материалов с поиском, фильтрами и сортировкой;
- оформление заявок студентом;
- просмотр и изменение статусов заявок преподавателем или администратором;
- добавление, редактирование и удаление материалов администратором;
- управление пользователями администратором;
- локальная база SQLite создается автоматически в `data/learning_materials.sqlite3`.

## Тестовые пользователи

- `admin` / `admin`
- `teacher` / `teacher`
- `student` / `student`

## Настройка VS Code (чтобы не было красных подчёркиваний)

1. Установите Python 3.12 с https://www.python.org/downloads/ (галочка **Add to PATH**).
2. Откройте проект: **File → Open Folder** → папка `uchebnye-materialy-project`  
   или файл `uchebnye-materialy-project.code-workspace`.
3. Пересоздайте окружение на Python 3.12:

```powershell
cd C:\Users\vange\Desktop\uchebnye-materialy-project
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

4. Выберите интерпретатор: `Ctrl+Shift+P` → **Python: Select Interpreter** →  
   `.\.venv\Scripts\python.exe` (должно быть **Python 3.12.x**).
5. Перезапустите анализ: `Ctrl+Shift+P` → **Pylance: Restart Language Server**, затем **Developer: Reload Window**.

Внизу справа в статус-баре должно быть: `Python 3.12.x ('.venv': venv)`.

> Python 3.14 часто даёт ложные красные подчёркивания в VS Code, хотя программа запускается. Для редактора лучше **3.12**.

## Запуск

```powershell
cd C:\Users\vange\Desktop\uchebnye-materialy-project
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m learning_materials.main
```

После первого запуска база данных создастся автоматически в файле `data/learning_materials.sqlite3`.

> Не используйте просто `python`, если он указывает на системный Python 3.14 без PyQt6.

## Быстрый запуск после установки

Если зависимости уже установлены:

```powershell
.venv\Scripts\python.exe -m learning_materials.main
```

Или двойным кликом по файлу `run_app.bat` (он тоже использует `.venv`).

## Если команда `python` не работает

Попробуйте заменить `python` на `py`:

```powershell
py -m venv .venv
py -m learning_materials.main
```
