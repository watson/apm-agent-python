ARG PYTHON_IMAGE 
FROM ${PYTHON_IMAGE}

WORKDIR /app
ADD . /app
