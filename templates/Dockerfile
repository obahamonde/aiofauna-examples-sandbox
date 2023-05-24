FROM python:3.7
ARG LOCAL_PATH
WORKDIR /app
COPY ${LOCAL_PATH}/requirements.txt /app
RUN pip install --upgrade pip \    
    pip install --no-cache-dir -r requirements.txt
COPY ${LOCAL_PATH} /app
CMD ["python", "main.py"]