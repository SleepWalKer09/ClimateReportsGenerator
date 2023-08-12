import unittest
from FrontStream import get_weather_data  # funcion que obtiene los datos climaticos 


# python -m unittest test_Streamlit.py

class TestFrontStream(unittest.TestCase):

    def test_get_weather_data_valid_city(self):
        # Test 1: ciudad valida
        data = get_weather_data('London')
        self.assertIn('name', data)
        self.assertEqual(data['name'], 'London')

    def test_get_weather_data_city_404(self):
        # Test 2: ciudad no existe en la API
        data = get_weather_data('CityABC')
        self.assertIsNone(data)
    
    def test_get_weather_data_number_city(self):
        # Test 3: ciudad con puros numeros
        data = get_weather_data('19728')
        self.assertIsNone(data)
    
    def test_get_weather_data_invalid_city(self):
        # Test 4: ciudad valida con numero
        data = get_weather_data('Orlando1')
        self.assertIsNone(data)

if __name__ == '__main__':
    unittest.main()

