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
