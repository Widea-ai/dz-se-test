import json
from datetime import date

class Actor:
    """
    Class Actor
    """
    def __init__(self, id, name):
        """
        Constructor
        :param id: int
        Actor Id
        :param name: string
        Actor's name
        """
        self.id = id
        self.name = name
        self.actions = []

    def debit(self, amount, rental_id):
        """
        Debit the actor related with a rental
        :param amount: int
        Amount of the debit
        :param rental_id:
        Rental id
        """
        self.actions.append(Action('debit', amount, rental_id))

    def credit(self, amount, rental_id):
        """
        Credit the actor related with a rental
        :param amount: int
        Amount of the credit
        :param rental_id:
        Rental id
        :return:
        """
        self.actions.append(Action('credit', amount, rental_id))

    def get_actions(self, rental_id):
        """
        Collect actions related with a rental
        :param rental_id: in
        Rental id
        """
        results = []
        for action in list(filter(lambda x: (x.rental_id == rental_id), self.actions)):
            results.append({
                'who': self.name,
                'type': action.type,
                'amount': action.amount
            })

        return results

class Action:
    """
    Class Action
    """
    def __init__(self, type, amount, rental_id):
        """
        Constructor
        :param type: string
        Action type
        :param amount: int
        Action amount
        :param rental_id: int
        Rental related with the action
        """
        self.type = type
        self.amount = amount
        self.rental_id = rental_id

class Car:
    """
    Class Car
    """
    def __init__(self, id, price_per_day, price_per_km):
        """
        Constructor
        :param id: int
        Car id
        :param price_per_day: int
        Car price per day
        :param price_per_km: int
        Car price per km
        """
        self.id = id
        self.price_per_day = price_per_day
        self.price_per_km = price_per_km

    def apply_discount(self, nb_days):
        """
        Apply a specific discount on the car depending on how many days the driver is going to use it
        :param nb_days: int
        Number of days the driver is going to use the car
        :return:
        Car price per day with discount
        """
        if nb_days > 1:
            discount = 0.9
        elif nb_days > 4:
            discount = 0.7
        elif nb_days > 10:
            discount = 0.5
        else:
            discount = 1

        return self.price_per_day * discount

class Rental:
    """
    Class Rental
    """
    def __init__(self, id, car_id, start_date, end_date, distance):
        """
        Constructor
        :param id: int
        Rental id
        :param car_id: int
        Car id related with rental
        :param start_date: string
        Start date of the rental
        :param end_date: string
        End date of the rental
        :param distance: int
        Disantce of the rental
        """
        self.id = id
        self.car_id = car_id
        tmp_date = start_date.split('-')
        self.start_date = date(int(tmp_date[0]), int(tmp_date[1]), int(tmp_date[2]))
        tmp_date = end_date.split('-')
        self.end_date = date(int(tmp_date[0]), int(tmp_date[1]), int(tmp_date[2]))
        self.distance = distance
        # computed
        self.nb_days = int((self.end_date - self.start_date).days)
        self.options = []

    def compute_price(self, car):
        """
        Calculate price for the rental
        :param car: Car
        Car object related with the rental
        """
        price_per_day = car.apply_discount(self.nb_days)
        self.price = (price_per_day * self.nb_days) + (car.price_per_km * self.distance)

    def keep_commission(self):
        """
        Calculate commission for the rental
        """
        if hasattr(self, 'price'):
            self.commission = self.price * 0.3
            self.insurance_fee = self.commission / 2
            self.assistance_fee = self.nb_days
            self.drivy_fee = self.commission - (self.insurance_fee + self.assistance_fee)
        else:
            raise Exception('You need to compute the price before the commission !')

    def get_bill(self):
        """
        Print bill for the rental
        :return: Dictionnary
        """
        return {
            'id': self.id,
            'price': self.price,
            'commission': {
                'insurance_fee': self.insurance_fee,
                'assistance_fee': self.assistance_fee,
                'drivy_fee': self.drivy_fee
            }
        }

    def get_options(self):
        """
        Get options related with the rental
        :return: Array
        Options
        """
        result = []
        for option in self.options:
            result.append(option.type)

        return result

class Option:
    """
    Class Option
    """
    def __init__(self, id, type):
        """
        Constructor
        :param id: int
        Option id
        :param type: string
        Option type
        """
        self.id = id
        self.type = type

class App:
    """
    Class App
    """
    def __init__(self, input):
        """
        Initialize objects used for the App
        :param input: Dictionnary
        """
        self.drivy = Actor(1, 'drivy')
        self.insurance = Actor(2, 'insurance')
        self.assistance = Actor(3, 'assistance')
        # Let's says that we have 1 owner and 1 driver
        self.owner = Actor(4, 'owner')
        self.driver = Actor(5, 'driver')

        self.cars = []
        for car in input['cars']:
            self.cars.append(Car(car['id'], car['price_per_day'], car['price_per_km']))

        self.rentals = []
        for rental in input['rentals']:
            self.rentals.append(Rental(rental['id'], rental['car_id'], rental['start_date'],
                                              rental['end_date'], rental['distance']))

        for option in input['options']:
            self.get_rental(option['rental_id']).options.append(Option(option['id'], option['type']))

    def compute_rentals(self):
        """
        Calculate rental price for each rentals
        """
        for rental in self.rentals:
            rental.compute_price(self.get_car(rental.car_id))
            rental.keep_commission()

    def generate_rental_bills(self):
        """
        Generate rental bills for each rentals
        :return: Dictionnary
        """
        results = {'rentals': []}
        for rental in self.rentals:
            results['rentals'].append(rental.get_bill())

        return results

    def compute_actions(self):
        """
        Compute actions for eache rentals
        """
        for rental in self.rentals:
            self.drivy.credit(rental.drivy_fee, rental.id)
            self.assistance.credit(rental.assistance_fee, rental.id)
            self.insurance.credit(rental.insurance_fee, rental.id)
            self.owner.credit(rental.price - rental.commission, rental.id)
            self.driver.debit(rental.price, rental.id)

    def generate_actions_report(self):
        """
        Generate action report for each rentals
        :return: Dictionnary
        """
        results = {'rentals': []}
        for rental in self.rentals:
            rental_actions = {'id': rental.id,
                              'options': rental.get_options(),
                              'actions': []}
            rental_actions['actions'].extend(self.drivy.get_actions(rental.id))
            rental_actions['actions'].extend(self.assistance.get_actions(rental.id))
            rental_actions['actions'].extend(self.insurance.get_actions(rental.id))
            rental_actions['actions'].extend(self.owner.get_actions(rental.id))
            rental_actions['actions'].extend(self.driver.get_actions(rental.id))
            results['rentals'].append(rental_actions)

        return results

    def get_car(self, car_id):
        """
        Get Car from Car list given an id
        :param car_id: int
        Car id
        :return: Car
        """
        car = list(filter(lambda x: (x.id == car_id), self.cars))[0]
        if car is None:
            raise Exception('There is no car with this id in car list')

        return car

    def get_rental(self, rental_id):
        """
        Get Rental from rental list given an id
        :param rental_id: int
        Rental id
        :return: Rental
        """
        rental = list(filter(lambda x: (x.id == rental_id), self.rentals))[0]
        if rental is None:
            raise Exception('There is no rental with this id in rental list')

        return rental

if __name__ == '__main__':
    # Read input.json
    input = json.load(open("data/input.json"))

    app = App(input)
    app.compute_rentals()
    app.compute_actions()
    output = app.generate_actions_report()

    with open('data/output.json', 'w') as output_file:
        json.dump(output, output_file)
