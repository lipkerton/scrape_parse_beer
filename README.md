# Как пользоваться? #
Установка виртуального окужения, активация, установка зависимостей (все делается внутри папки с проектом):

**MacOS/Linux**
```Bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
playwright install
```
**Windows**
```PowerShell
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt
playwright install
```
Есть вероятность что Windows откажет в исполнении файла `.\venv\Scripts\activate` - так происходит, потому что в вашем Windows по-умолчанию стоит запрет на выполнение стрёмных скриптов. Я не настаиваю, но его можно снять, если ввести:
```PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
```
После снятия запрета просто повторите в папке проекта команду `.\venv\Scripts\activate` и все дальнейшие действия.
