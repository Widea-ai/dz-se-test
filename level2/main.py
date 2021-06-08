import json
from datetime import date

class Car:
    def __init__(self, id, price_per_day, price_per_km):
        self.id = id
        self.price_per_day = price_per_day
        self.price_per_km = price_per_km

class Rental:
    def __init__(self, id, car_id, start_date, end_date, distance):
        self.id = id
        self.car_id = car_id
        tmp_date = start_date.split('-')
        self.start_date = date(int(tmp_date[0]), int(tmp_date[1]), int(tmp_date[2]))
        tmp_date = end_date.split('-')
        self.end_date = date(int(tmp_date[0]), int(tmp_date[1]), int(tmp_date[2]))
        self.distance = distance

class App:
    def __init__(self, input):
        self.cars = []
        for car in input['cars']:
            self.cars.append(Car(car['id'], car['price_per_day'], car['price_per_km']))

        self.rentals = []
        for rental in input['rentals']:
            self.rentals.append(Rental(rental['id'], rental['car_id'], rental['start_date'], rental['end_date'], rental['distance']))

    def get_car(self, car_id):
        return list(filter(lambda x: (x.id == car_id), self.cars))[0]

    def compute_rental_prices(self):
        results = {'rentals': []}
        for rental in self.rentals:
            car = self.get_car(rental.car_id)
            nb_days = int((rental.end_date - rental.start_date).days)
            price_per_day = car.price_per_day * self.get_discount(nb_days)
            price = (price_per_day * nb_days) + (car.price_per_km * rental.distance)
            results['rentals'].append({'id': rental.id, 'price': price})

        return results

    @staticmethod
    def get_discount(nb_days):
        discount = None
        if nb_days > 1:
            discount = 0.9
        elif nb_days > 4:
            discount = 0.7
        elif nb_days > 10:
            discount = 0.5
        else:
            discount = 1

        return discount


if __name__ == '__main__':
    # Read input.json
    input = json.load(open("data/input.json"))

    app = App(input)
    output = app.compute_rental_prices()

    with open('data/output.json', 'w') as output_file:
        json.dump(output, output_file)
