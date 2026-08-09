# ============================================================
#  calculator.py  –  A beginner-friendly Python calculator
#  Concepts covered: functions, parameters, return values,
#                    if/elif/else, while loop, input(), float()
# ============================================================


# ------ BASIC OPERATIONS ------
# A "function" is a reusable block of code.
# "def" defines it, "return" sends the result back.

def add(a,b):
    return a+b

def sub(a,b):
    return a-b

def mul(a,b):
    return a*b

def div(a,b):
    return a/b

def mod(a,b):
    return a%b

def pwr(a,b):
    return a**b

def switch(a,b,op):
    match op:
        case 1:
            c = add(a,b)
        case 2:
            c = sub(a,b)
        case 3:
            c = mul(a,b)
        case 4:
            c = div(a,b)
        case 5:
            c = mod(a,b)
        case 6:
            c = pwr(a,b)
        case _:
            return "Invalid choice"
    return c

def show_menu():
    print("Select your choice from the below:")
    print("1) Add", end="\t")
    print("2) Sub", end="\t")
    print("3) Mul", end="\t")
    print("4) Div", end="\t")
    print("5) Mod", end="\t")
    print("6) Pow", end="\t")
    print("0) Quit")

def main():
    while True:        
        show_menu()
        try:
            op = int(input("What do you want to calculate?"))
        except ValueError:
            print("Enter valid choice")
            continue

        if op==0:
            print("Exit")
            break

        if op not in range(1,6+1):
            print("Invalid operation")
            continue

        a = float(input("Enter first number:"))
        b = float(input("Enter second number:"))
        if (op==4 or op==5) and b <= 0:
            print("Divide by zero issue")
        else: 
            c = switch(a,b,op)
            print(f"Result = {c:.4f}") # show 4 decimal places

# This is a Python convention — it means "only run main() if this file
# is executed directly, not when it's imported by another file."
if __name__ == "__main__":
    main()
