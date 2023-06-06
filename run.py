#!venv/bin/python3
from ecss import ecss

# Start flask app
if __name__ == "__main__":
    ecss.run(debug=True, host="0.0.0.0")
