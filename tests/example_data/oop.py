class Animal:
    # Class attribute (shared by all instances)
    kingdom = "Animalia"

    def __init__(self, name, age):
        # Instance attributes
        self.name = name
        self.age = age

    def speak(self) -> str:
        return "Some generic animal sound"

    def info(self):
        return f"{self.name} is {self.age} years old."


class Dog(Animal):
    def __init__(self, name, age, breed):
        # Initialize attributes from the parent class
        super().__init__(name, age)
        self.breed = breed

    def speak(self):
        # Override the parent method
        return "Woof!"

    def fetch(self):
        return f"{self.name} is fetching the ball."


class Cat(Animal):
    def __init__(self, name, age, indoor=True):
        super().__init__(name, age)
        self.indoor = indoor

    def speak(self):
        return "Meow!"


class GuideDog(Dog):
    def __init__(self, name, age, breed, owner):
        super().__init__(name, age, breed)
        self.owner = owner

    def guide(self):
        return f"{self.name} is guiding {self.owner}."
