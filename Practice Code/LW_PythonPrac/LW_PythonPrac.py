class PracClass:
    #Class in python w/ arrtibute mess
    mess = "Hello World!"
    num = 43


def my_fun(x):
    #Function in python that has class as parameter and prints the mess
    print(x.mess)


ex = PracClass()

my_fun(ex)  #calls function w/ parameter ex
print(ex.num)   #prints attribute of class

#reading from file

filename = input("Enter the name of the file: ")

file = open(filename)
print(file.read())