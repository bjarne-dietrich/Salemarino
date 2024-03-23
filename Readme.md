# Salemarino

This is a Flask project for Storing and Getting Images from the Web Browser.

## Requirements

- Python (version 3.11.7)
- Docker (optional)

## Installation

### Without Docker

1. Clone the repository:

    ```bash
    git clone https://github.com/bjarne-dietrich/Salemarino.git
    ```

2. Navigate to the project directory:

    ```bash
    cd Salemarino
    ```

3. Create a virtual environment (optional but recommended):

    ```bash
    python3 -m venv venv
    ```

4. Activate the virtual environment:

    - **On Windows**:

        ```bash
        venv\Scripts\activate
        ```

    - **On macOS and Linux**:

        ```bash
        source venv/bin/activate
        ```

5. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### With Docker

1. Clone the repository:

    ```bash
    git clone https://github.com/bjarne-dietrich/Salemarino.git
    ```

2. Navigate to the project directory:

    ```bash
    cd Salemarino
    ```

## Usage

### Running without Docker

1. Make sure you are in the project directory and your virtual environment is activated (if you created one).

2. Run the Flask application:

    ```bash
    python app.py
    ```

3. Access the application in your web browser at `http://localhost:5000`.

### Running with Docker

1. Make sure you have Docker installed and running on your system.

2. Build the Docker image:

    ```bash
    docker build -t salemarino .
    ```

3. Run the Docker container:

    ```bash
    docker run -p 5001:5001 -v ./data:/app/data salemarino
    ```

4. Access the application in your web browser at `http://localhost:5000`.

## Notes

- If you encounter any issues or have questions, please feel free to open an issue on GitHub.
- See LICENSE.md for License Information
