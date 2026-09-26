FROM nginx:alpine

# Удаляем дефолтный конфиг Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Копируем наш кастомный конфиг проксирования
COPY nginx.conf /etc/nginx/conf.d/

# Копируем файлы интерфейса в папку раздачи статики
COPY index.html /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

EXPOSE 80
