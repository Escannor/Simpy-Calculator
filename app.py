from flask import Flask, render_template, url_for, request, redirect
from Scipi7 import funcion_objetivo, ecuacion
import matplotlib.pyplot as plt
from scipy.optimize import linprog
import numpy as np
import os
#import shutil
import base64

# https://simpycalculator.herokuapp.com/

app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        restricciones = int(request.form['frestricciones'])
        return redirect(url_for('params_func', res=restricciones))

    else:
        return render_template('index.html')


@app.route('/params/<int:res>', methods=["POST", "GET"])
def params_func(res):
    print("Entra a params")
    if request.method == "POST":
        fx1 = []
        fx2 = []
        fec = []
        fres = []

        foptimizar = request.form["foptimizar"]
        fox1 = float(request.form["fox1"])
        fox2 = float(request.form["fox2"])

        for i in range(1, res+1):
            fx1.append(float(request.form[str(i) + "fx1"]))
            fx2.append(float(request.form[str(i) + "fx2"]))
            fec.append(request.form[str(i) + "fec"])
            fres.append(float(request.form[str(i) + "fres"]))

        x_lin = 1000
        x_vals = np.linspace(0, x_lin, x_lin)  # 10 valores entre 0 y 800

        restricciones = []
        A_ub = []
        b_ub = []
        A_eq = []
        b_eq = []

        c = funcion_objetivo(fox1, fox2, foptimizar)  # (5, 4, 'max')  #si es maximo hay que pasarlo a negativo y tambien su resultado

        for i in range(res):
            restricciones.append(ecuacion(fx1[i], fx2[i], fec[i], fres[i], x_vals))

        for r in restricciones:
            #print(r.type_ec)
            if r.type_ec == 'ub':
                A_ub.append(r.X)
                b_ub.append(r.result)
            else:
                A_eq.append(r.X)
                b_eq.append(r.result)

        if (len(A_eq) != 0) and (len(A_ub) != 0):
            print("Hay equidades y mayor/menor")
            res = linprog(c.X, A_ub, b_ub, A_eq, b_eq, bounds=(0, None))
            print(c.X, A_ub, b_ub, A_eq, b_eq)
            print(res)
            print("Valor óptimo: ", np.absolute(res.fun), "\nX: ", res.x)
        elif (len(A_ub) != 0):
            print("No hay equidades")
            res = linprog(c.X, A_ub, b_ub, bounds=(0, None))
            print(c.X, A_ub, b_ub)
            print(res)
            print("Valor óptimo: ", np.absolute(res.fun), "\nX: ", res.x)
        elif (len(A_eq) != 0):
            print("No hay equidades")
            res = linprog(c.X, A_eq=A_eq, b_eq=b_eq, bounds=(0, None))
            print(c.X, A_eq, b_eq)
            print(res)
            print("Valor óptimo: ", np.absolute(res.fun), "\nX: ", res.x)

        plt.figure(figsize=(10, 8))
        # print("Valores de y")
        for i, r in enumerate(restricciones):
            plt.plot(x_vals, r.y, label=r.get_label())
            # print(r.y)
        #    if i == 0:
        #        Ymin = r.y
        #        Ymax = r.y
        #    else:
        # Ymin Ymax
        #        if r.ec == '>=':
        #            Ymin = np.minimum(Ymin, r.y)
        #        elif r.ec == '<=':
        #            Ymax = np.maximum(Ymax, r.y)

        print(res.message)
        print(f"Se encontro solucion: {res.success}")

        if foptimizar == 'max':
            maxim = (res.x[0] + res.x[1]) * 1.7
            plt.axis(xmin=0, ymin=0, xmax=maxim, ymax=maxim)
        else:
            maxim = (res.x[0] + res.x[1]) * 2.5
            plt.axis(xmin=0, ymin=0, xmax=maxim, ymax=maxim)

        if res.success == True:
            plt.plot(x_vals, (np.absolute(res.fun) - (c.x1 * x_vals)) / c.x2, '--',
                     label="Z: " + c.get_label() + "{0:.4f}".format(np.absolute(res.fun)))
            plt.plot(res.x[0], res.x[1], 'b*', markersize=12,
                     label='$x_1 = ' + "{0:.4f}".format(res.x[0]) + ',  x_2 = ' + "{0:.4f}".format(res.x[1]) + '$')

            # Región factible
            # y3 = np.maximum(restricciones[0].y, restricciones[2].y)
            # y4 = np.maximum(restricciones[0].y, restricciones[1].y)
            # plt.fill_between(x_vals, Ymax, Ymin, alpha=0.15, color='b')

            xd = np.linspace(0, res.x[0] * 10, 1000)
            yd = np.linspace(0, res.x[1] * 10, 1000)
            a, b = np.meshgrid(xd, yd)

            constraint = []
            for r in restricciones:
                if (r.ec == '>='):
                    #print(">=")
                    constraint.append((r.x2 * b) + (r.x1 * a) >= r.r)
                elif (r.ec == '<='):
                    print("<=")
                    constraint.append((r.x2 * b) + (r.x1 * a) <= r.r)
                else:
                    print("==")
                    constraint.append((r.x2 * b) + (r.x1 * a) == r.r)

            total_constraint = constraint.pop(0)
            for c in constraint:
                total_constraint = total_constraint & c

            # ((constraint[0]) & (constraint[1]) & (constraint[2]) & (constraint[3]) & (constraint[4]) & (constraint[5]) & (constraint[6]) & (constraint[7]) & (constraint[8]) & (constraint[9]))
            plt.imshow(total_constraint.astype(int),
                       extent=(a.min(), a.max(), b.min(), b.max()), origin="lower",
                       cmap="Purples", alpha=0.15)  # "Greys"

        plt.title('Optimización lineal')
        plt.margins(x=40, y=40)
        plt.legend()
        plt.savefig('solucion_grafica')
        plt.show()
        #TODO shutil.move("solucion_grafica.png", "Images/solucion_grafica.png")

        if res.success == True:
            #return f"La solucion óptima es de: {np.absolute(res.fun)} Siendo x1: {res.x[0]}, x2: {res.x[1]}"
            #return f"fopt: {foptimizar}  fx1:{fox1} fx2:{fox2} fx1:{fx1} fx2:{fx2} fec:{fec} fres:{fres}"
            return redirect(url_for('solucion', resultado=np.absolute(res.fun), x1=res.x[0], x2=res.x[1]))

        else:
            return f"No se encontro solución para este problema"

    else:
        return render_template('funcion.html', restricciones=res)



@app.route('/solucion', defaults={'resultado': 0, 'x1': 0, 'x2': 0})
@app.route('/solucion/<resultado>/<x1>/<x2>', methods=["POST", "GET"])
def solucion(resultado, x1, x2):
    with open("solucion_grafica.png", "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
        my_string = str(my_string)[2:-1]
        print(my_string)
    #TODO full_filename = os.path.join('static', 'solucion_grafica.png')
        return render_template('solucion.html', imageb64=my_string, resultado=resultado, x1=x1, x2=x2)


@app.route('/chino')
def chino():
    full_filename = os.path.join('static', 'Chino.jpeg')
    return render_template('solucion.html', graphic_image = full_filename)



if __name__ == '__main__':
    app.run()
