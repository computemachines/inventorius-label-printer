from flask import Flask
import printer

app = Flask(__name__)


@app.route("/print/<code>")
def print_get(code):
    printer.print_code(code, "/tmp/printer")
    return f"{code} sent to printer"


if __name__ == "__main__":
    app.run(port=8899)
