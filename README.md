# Furriel Digital

> O sistema mostra e gera relatórios mensais dos militares que não fizeram uso do auxilio transporte por algum motivo. Motivos como serviço, missão, dispensa e outros...
> O objetivo do sistema é auxiliar o furriel das Subunidades no controle mensal de descontos do auxilio transporte dos militares.

# Súmario

instalar tailwindcss compilado
remover browserreload
banco de dados, siconef, para sisconef26

pip download -r requirements.txt --python-version 313 --platform win_amd64 --only-binary=:all: -d pack

pip install --no-index --find-links=pack -r requirements.txt

------- 


tailwindcss.exe -i ./furriel/static/furriel/input.css -o ./furriel/static/furriel/output.css --watch --content "./**/*.html"