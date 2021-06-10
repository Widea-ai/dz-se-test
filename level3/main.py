import json
from datetime import date

class Car:
    def __init__(self, id, price_per_day, price_per_km):
        self.id = id
        self.price_per_day = price_per_day
        self.price_per_km = price_per_km

    def apply_discount(self, nb_days):
        if nb_days > 1:
            discount = 0.9
        elif nb_days > 4:
            discount = 0.7
        elif nb_days > 10:
            discount = 0.5
        else:
            discount = 1

        self.price_per_day = self.price_per_day * discount

class Rental:
    def __init__(self, id, car, start_date, end_date, distance):
        self.id = id
        self.car = car
        tmp_date = start_date.split('-')
        self.start_date = date(int(tmp_date[0]), int(tmp_date[1]), int(tmp_date[2]))
        tmp_date = end_date.split('-')
        self.end_date = date(int(tmp_date[0]), int(tmp_date[1]), int(tmp_date[2]))
        self.distance = distance
        # computed
        self.nb_days = int((self.end_date - self.start_date).days)

    def compute_price(self):
        self.car.apply_discount(self.nb_days)
        self.price = (self.car.price_per_day * self.nb_days) + (self.car.price_per_km * self.distance)

    def keep_commission(self):
        if hasattr(self, 'price'):
            commission = self.price * 0.3
            self.insurance_fee = commission / 2
            self.assistance_fee = self.nb_days
            self.drivy_fee = commission - (self.insurance_fee + self.assistance_fee)
        else:
            raise Exception('You need to compute the price before the commission !')

    def get_bill(self):
        return {
            'id': self.id,
            'price': self.price,
            'commission': {
                'insurance_fee': self.insurance_fee,
                'assistance_fee': self.assistance_fee,
                'drivy_fee': self.drivy_fee
            }
        }

class App:
    def __init__(self, input):
        self.cars = []
        for car in input['cars']:
            self.cars.append(Car(car['id'], car['price_per_day'], car['price_per_km']))

        self.rentals = []
        for rental in input['rentals']:
            self.rentals.append(Rental(rental['id'], self.get_car(rental['car_id']), rental['start_date'], rental['end_date'], rental['distance']))

    def get_car(self, car_id):
        return list(filter(lambda x: (x.id == car_id), self.cars))[0]

    def get_rental_prices(self):
        results = {'rentals': []}
        for rental in self.rentals:
            rental.compute_price()
            rental.keep_commission()
            results['rentals'].append(rental.get_bill())

        return results

if __name__ == '__main__':
    # Read input.json
    input = json.load(open("data/input.json"))

    app = App(input)
    output = app.get_rental_prices()

    with open('data/output.json', 'w') as output_file:
        json.dump(output, output_file)
