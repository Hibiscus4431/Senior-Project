#Paige Smith

#Practice code for Python
#write a basic class outline, and a function to print something 

#class outline
class Student:
    #constructor
    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade

    #function to print student info
    def printStudent(self):
        print("Name: " + self.name)
        print("Age: " + str(self.age))
        print("Grade: " + str(self.grade))

#student object
janeDoe = Student("Jane Doe", 16, 10)
janeDoe.printStudent()