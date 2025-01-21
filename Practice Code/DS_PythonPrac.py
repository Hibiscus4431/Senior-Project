# Test Program

#--------------------------------------------------
# Note: Must Run in "Dedicated Terminal" to handle input
#--------------------------------------------------

# Function Example

def greet_user(name):
    print(f"Hello, {name}.")


# Class Example
class Counter:

    def __init__(self, start = 0):
        self.value = start

    def increment(self):
        self.value += 1

    def __str__(self):
        return f"Counter value: {self.value}"

# Main Code Block  
if __name__ == "__main__":
    user_name = input("Enter your name: ")

# Call the Function
    greet_user(user_name)

# Instantiate the Object
    counter = Counter()

    print(counter)

# Loop
    for _ in range(3):
        counter.increment()
        print(counter)