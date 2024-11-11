# FastAPI POC

This project is a proof of concept (POC) for using FastAPI, a modern, fast (high-performance), web framework for building APIs with Python 3.7+.

### Please expect iterative/evolving architecture for this POC as we keep on adding various use-cases.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/shubhammetkarlrn/AI-course-creator-POC-fastAPI.git
```

2. Navigate to the project directory:

```bash
cd fastapi-poc
```

3. Create a virtual environment:

```bash
python3 -m venv venv
```

4. Activate the virtual environment:

```bash
source venv/bin/activate
```

5. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

To start the FastAPI server, run the following command:

```bash
uvicorn main:app --reload
```

You can then access the API at `http://localhost:8000`.

## API Documentation

The API documentation is automatically generated using Swagger UI. You can access it at `http://localhost:8000/docs`.

## I/P - O/P

In the root directory, there will reside course.xml(i/p) & output.xml(o/p), also as we're incrementally adding new templates course.xml file will be versionized (i.e older course files will be assigned as course_vX.xml) & the latest one will be course.xml.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
