from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        try:
            a = float(request.form["a"])
            b = float(request.form["b"])
            op = request.form["op"]

            if op == "+":
                result = a + b
            elif op == "-":
                result = a - b
            elif op == "*":
                result = a * b
            elif op == "/":
                result = a / b
        except:
            result = "Ошибка 😢"

    return render_template("calculator.html", result=result)


@app.route("/timer")
def timer():
    return render_template("timer.html")


@app.route("/converter", methods=["GET", "POST"])
def converter():
    result = None
    if request.method == "POST":
        value = float(request.form["value"])
        result = value * 0.001  # метры → километры
    return render_template("converter.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
