### Запуск проекта
1. Запустите Docker Desktop
2.  Перейдите в директорию проекта, соберите docker-образ и запустите контейнеры:
```bash
docker-compose up --build
```
3. Далее для запуска проекта используйте эту же команду, но без "--build":
```bash
docker-compose up
```
4. Перейдите на http://127.0.0.1:8501 и протестируйте фронтенд (streamlit)
5. Протестируйте backend через curl: 
```
curl -X 'GET' \
  'http://127.0.0.1:8000/health' \
  -H 'accept: application/json'
```
Или воспользуйтесь http://127.0.0.1:8000/docs


### Запуск и настройка сервера
1. Установить докер:
```bash
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```
```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
2. Установить docker-compose:
```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```
3. Установить git:
```bash
sudo apt update
sudo apt install git
```
4. Склонируйте репозиторий
5. Запустите сборку:
```bash
docker-compose up --build
```
