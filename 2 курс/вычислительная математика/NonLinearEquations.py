from sympy import diff
def get_formula():
    global formula
    formula = input('\nВведите выражение')


def f(x):
    return eval(formula)

def ff(x):
    diff_raw = f(x)
    return diff(diff_raw)



def mdp(lower_limit, upper_limit, accuracy):
    while abs(upper_limit-lower_limit) > accuracy:
        x = (lower_limit+upper_limit)/2
        if f(lower_limit)*f(x) < 0:
            upper_limit = x
        else:
            lower_limit = x
    return x


def hrd(lower_limit, upper_limit, accuracy):
    while True:
        x = lower_limit - f(lower_limit)*((upper_limit-lower_limit)/(f(upper_limit)-f(lower_limit)))
        if f(lower_limit)*f(x) <= 0:
            upper_limit = x
        else:
            lower_limit = x
        if abs(f(x)) <= accuracy:
            return x


def Newton(approximation, accuracy):
    while True:
        approximation = approximation - f(approximation)/ff(approximation)
        if abs(f(approximation))<=accuracy:
            return approximation


def main():
    print("\nДобро пожаловать в калькулятор нелинейных уравнений, данная программа программно реализует метод ньютона,"
          " метод деления на два отрезка, метод хорд ")
    choise = int(input('\nВыберите метод:\n1 - метод деления на два отрезка\n2 - метод хорд\n 3 - метод ньютона'))
    match choise:
        case 1:
            lower_limit = float(input("\nВведите левую границу интервала: "))
            upper_limit = float(input("\nВведите правую границу интервала: "))
            accuracy = float(input("\nВведите точность решения: "))
            get_formula()
            answer = mdp(lower_limit, upper_limit, accuracy)
            print(f"\nx = {answer},\n equation = {formula}")
        case 2:
            lower_limit = float(input("\nВведите левую границу интервала: "))
            upper_limit = float(input("\nВведите правую границу интервала: "))
            accuracy = float(input("\nВведите точность решения: "))
            get_formula()
            answer = hrd(lower_limit, upper_limit, accuracy)
            print(f"\nx = {answer},\n equation = {formula}")
        case 3:
            approximation = float(input("\nВведите начальное приближение: "))
            accuracy = float(input("\nВведите точность решения: "))
            get_formula()
            answer = Newton(approximation, accuracy)
            print(f"\nx = {answer},\n equation = {formula}")



