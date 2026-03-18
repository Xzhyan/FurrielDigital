instalar tailwindcss compilado
remover browserreload
banco de dados, siconef, para sisconef26

pip download -r requirements.txt --python-version 313 --platform win_amd64 --only-binary=:all: -d pack

pip install --no-index --find-links=pack -r requirements.txt