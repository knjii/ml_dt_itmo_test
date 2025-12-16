### Проект по дисциплине "Машинное обучение"
Суть проекта: Разработать модель бинарной классификации для прогнозирования приобретения автомобильной страховки.

### Команда проекта
Лапытова Екатерина - Написание API, тестирование
Аксёнова Ирина -  Frontend, Оформление презентации
Шугаев Максим - Team Leader, Инференс, Backend + Docker
Новикова Виктория - Разработка модели "Random Forest", офорление репозитория
Нарыжный Даниил - Анализ данных, Пайплайны обучены, подбор гиперпараметров

### Задачи
*Бинарная классификация**  
Цель: спрогнозировать, купит ли страховой продукт конкретный человек.  
Целевая переменная: `response`  
Ключевая метрика: **F1-score**

### Exploratory Data Analysis
Анализ проводился в Kaggle Notebook. Были выполнены следующие ключевые шаги:
1.  **Первичный осмотр данных:** загрузка данных, оценка размеров, проверка типов столбцов и наличия пропущенных значений.
2.  **Статистическое описание:** анализ распределения числовых и категориальных признаков.
3.  **Визуальный анализ:** построение графиков для изучения взаимосвязей между признаками и целевой переменной (`response`).
4.  **Препроцессинг и feature engineering:** подготовка данных для обучения моделей (кодирование категориальных переменных, масштабирование).
5.  **Анализ важности признаков:** После построения модели LightGBM была проанализирована вклад каждого признака в прогноз. Это позволило выявить наиболее значимые факторы, влияющие на решение клиента.

Ключевой вывод:** На решение о покупке страховки наиболее сильно влияют факторы, связанные с **историей и состоянием автомобиля (Vehicle_Damage, Vehicle_Age)**, а также **индивидуальные характеристики и история клиента (Vintage, Previously_Insured, Age)**.

## Исследование моделей (ML Research)
В ходе проекта были проанализированы следующие модели:
- Логистическая регрессия
- Случайный лес (Random Forest)
- Бустинги:
  - LightGBM
  - CatBoost
  - XGBoost  
Лучшая модель: **LightGBM** с F1-score = 0.494272

## Исследование моделей (ML Research)

В ходе проекта были проанализированы следующие модели:

- Логистическая регрессия
- Случайный лес (Random Forest)
- Бустинги:
  - LightGBM
  - CatBoost
  - XGBoost

Лучшая модель: **LightGBM** с F1-score = 0.494

## Архитектура проекта
### Frontend
- Реализован на **Python + Streamlit**
- Port: `8501`
- Интерфейс для ввода данных и получения прогнозов
- Получает URL через environment

### Backend
- Реализован на **FastAPI**
- Port: `8000`
- Docker-образ на базе **Python 3.11-slim** с библиотекой LightGBM
- Frontend и Backend связаны через `depends`
- Прогнозы генерируются итеративно и отправляются на API через `requests.post`

### Тестирование
**Механика: Прогнозы генерируются итеративно (iterrows) и отправляются на API (requests.post) для получения результата модели**
Модели были протестированы на тестовых данных. Были получены слкдующие метрики: F1 Score, ROC, Recall, Precision

*** Конфигурацмя проект***
Настройки проекта управляются через файл config.yaml в корне проекта. Этот файл содержит ключевые пути, URL-адреса

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
