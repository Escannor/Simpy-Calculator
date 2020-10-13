import matplotlib.pyplot as plt
from scipy.optimize import linprog
import numpy as np
import os
import shutil


class funcion_objetivo():
    def __init__(self, x1, x2, opt):
        self.x1 = x1
        self.x2 = x2
        if opt == 'min':
            self.X = [self.x1, self.x2]
        elif opt == 'max':
            self.X = [self.x1*-1, self.x2*-1]

    def get_label(self):
        return '$' + str(self.x1) + ' x_1 + (' + str(self.x2) + ') x_2 = ' + '$'

class ecuacion():  #3 + 4 >= 2  [0, ... , 1000]
    def __init__(self, x1, x2, ec, r, linspace):
        self.x1 = x1
        self.x2 = x2
        self.ec = ec
        self.r = r

        self.x_values = self.x1*linspace

        if self.x2 != 0:
            self.y = ((self.r - self.x_values) / self.x2)
        else:
            self.y = self.r - self.x_values

        if self.ec == '>=':
            self.type_ec = 'ub'
            self.X = [self.x1 * (-1), self.x2 * (-1)]
            self.result = self.r * (-1)
        elif self.ec == '<=':
            self.type_ec = 'ub'
            self.X = [self.x1, self.x2]
            self.result = self.r
        else:
            self.type_ec = 'eq'
            self.X = [self.x1, self.x2]
            self.result = self.r

    def get_label(self):
        if self.ec == '>=':
            return '$' + str(self.x1) + 'x_1 + (' + str(self.x2) + ')x_2 \geq ' + str(self.r) + '$'
        elif self.ec == '<=':
            return '$' + str(self.x1) + 'x_1 + (' + str(self.x2) + ')x_2 \leq ' + str(self.r) + '$'
        else:
            return '$' + str(self.x1) + 'x_1 + (' + str(self.x2) + ')x_2 = ' + str(self.r) + '$'


if __name__ == '__main__':
    x_lin = 1000
    x_vals = np.linspace(0, x_lin, (2*x_lin)//3)  # 10 valores entre 0 y 800

    restricciones = []
    A_ub = []
    b_ub = []
    A_eq = []
    b_eq = []

    x1, x2, opt = input("Ingresa la funcion objetivo: ").split()
    c = funcion_objetivo(float(x1), float(x2), opt)  #(5, 4, 'max')  #si es maximo hay que pasarlo a negativo y tambien su resultado

    num_restricciones = int(input("Cuantas restricciones? "))
    for i in range(num_restricciones):
        x1, x2, ec, resultado = input("ec{i}").split()
        restricciones.append(ecuacion(float(x1), float(x2), ec, float(resultado), x_vals))

    #restricciones.append(ecuacion(6, 4, '<=', 24, x_vals))
    #restricciones.append(ecuacion(1, 2, '<=', 6, x_vals))
    #restricciones.append(ecuacion(-1, 2, '<=', 1, x_vals))
    #restricciones.append(ecuacion(0, 2, '<=', 2, x_vals))

    # c = funcion_objetivo(-4, -6)  #si es maximo hay que pasarlo a negativo

    # restricciones.append(ecuacion(3, 2, '<=', 50, x_vals))
    # restricciones.append(ecuacion(3, 4, '<=', 40, x_vals))


    #c = funcion_objetivo(0.3, 0.9)

    #restricciones.append(ecuacion(1, 1, '>=', 800, x_vals))
    #restricciones.append(ecuacion(0.21, -0.3, '<=', 0, x_vals))
    #restricciones.append(ecuacion(0.03, -0.01, '>=', 0, x_vals))

    for r in restricciones:
        print(r.type_ec)
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
    print("Valores de y")
    for i,r in enumerate(restricciones):
        plt.plot(x_vals, r.y, label=r.get_label())
        #print(r.y)
        if i == 0:
            Ymin = r.y
            Ymax = r.y
        else:
            #Ymin Ymax
            if r.ec == '>=':
                Ymin = np.minimum(Ymin, r.y)
            elif r.ec == '<=':
                Ymax = np.maximum(Ymax, r.y)

    print(res.message)
    print(f"Se encontro solucion: {res.success}")

    if opt == 'max':
        plt.axis(xmin=0, ymin=0, xmax=res.x[0] * 1.7, ymax=res.x[1] * 1.7)
    else:
        plt.axis(xmin=0, ymin=0, xmax=res.x[0] * 2.5, ymax=res.x[1] * 2.5)

    if res.success == True:
        plt.plot(x_vals, (np.absolute(res.fun) - (c.x1 * x_vals)) / c.x2, '--', label="Z: "+c.get_label()+"{0:.4f}".format(np.absolute(res.fun)))
        plt.plot(res.x[0], res.x[1], 'b*', markersize=12, label='$x_1 = '+"{0:.4f}".format(res.x[0])+',  x_2 = ' + "{0:.4f}".format(res.x[1]) + '$')

        # Región factible
        #y3 = np.maximum(restricciones[0].y, restricciones[2].y)
        #y4 = np.maximum(restricciones[0].y, restricciones[1].y)
        plt.fill_between(x_vals, Ymax, Ymin, alpha=0.15, color='b')


    plt.title('Optimización lineal')
    plt.margins(x=40, y=40)
    plt.legend()
    plt.savefig('solucion_grafica')
    plt.show()
    shutil.move("templates/solucion_grafica.png", "static/solucion_grafica.png")