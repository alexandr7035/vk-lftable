FROM python:3

# Directory for app files
ENV APP /vk-lftable
RUN mkdir $APP
WORKDIR $APP

# Copy file with python dependencies
COPY requirements.txt .

# Set timezone
RUN cp /usr/share/zoneinfo/Europe/Minsk /etc/localtime

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy all the app files to workdir
COPY . .

# Run the app
#CMD ["gunicorn", "vk-lftable:app", "--bind", "127.0.0.1:5000"]
CMD ["gunicorn", "vk-lftable:app", "--bind", "0.0.0.0:5000"]
