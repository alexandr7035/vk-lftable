FROM python:3.7.4

# Directory for app files
ENV APP /vk-lftable
RUN mkdir $APP
WORKDIR $APP

# Copy file with python dependencies
COPY requirements.txt .

# Set timezone
RUN echo 'Europe/Minsk' > /etc/timezone
RUN cp /usr/share/zoneinfo/Europe/Minsk /etc/localtime

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy all the app files to workdir
COPY . .

# Run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
