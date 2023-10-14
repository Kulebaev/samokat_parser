FROM joyzoursky/python-chromedriver:latest

WORKDIR /src

# Установка Google Chrome и зависимостей
RUN apt-get update && \
    apt-get install -y wget dbus-x11 libexif12 && \
    apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 1397BC53640DB551 && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean -y

# Установка ChromeDriver
RUN wget -O chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/linux64/chromedriver-linux64.zip
RUN unzip -d /usr/local/bin chromedriver.zip

# Удаление старого файла 
RUN rm /usr/local/bin/chromedriver
RUN mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Установка Python-зависимостей
COPY requirements.txt /src
RUN pip install -r requirements.txt

COPY . /src

# Команда для запуска
CMD ["python", "main.py"]
