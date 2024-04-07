def fix_json(etalon_json: str, generated_json: str):
    """
    Добавляет пропущенные параметры к сгенерируемому json, которые не удалось найти в тексте
    """
    try:
        generated_json = eval(generated_json.replace('undefined', '').replace('null', '""'))
        return {key: (generated_json[key] if key in generated_json.keys() else '') for key in etalon_json.keys()}
    except:
        return {key: '' for key in etalon_json.keys()}

class NER:
    def __init__(self):
        # Счетчик ошибок для покупки билетов по каждому атрибуту
        tickets_error_counter = {
            'departure_city': 0, 
            'arrival_city': 0, 
            'departure_date': 0, 
            'return_date': 0
        }

        # Счетчик ошибок для бронирования отелей по каждому атрибуту
        booking_error_counter = {
            'city': 0, 
            'hotel': 0, 
            'date': 0, 
            'guests': 0,
            'days': 0
        }

        # Шаблон атрибутов для билетов на самолет
        tickets_template = """
            - departure_city
                Описание: город отправления на самолете.
                Тип данных: str
            - arrival_city
                Описание: город прибытия на самолете.
                Тип данных: str
            - departure_date
                Описание: дата отправления из города отправления.
                Тип данных: date в формате day-month-year 
            - return_date
                Описание: дата возвращения из города прибытия.
                Тип данных:  date в формате day-month-year
        """
        
        # Шаблон атрибутов для бронирования отелей
        booking_template = """
            - city
                Описание: город расположения отеля.
                Тип данных: str
            - hotel
                Описание: название отеля.
                Тип данных: str
            - date
                Описание: дата заселения в отель.
                Тип данных: date в формате day-month-year
            - guests
                Описание: количество гостей для проживания.
                Тип данных: int
            - days
                Описание: количество дней пребывания в отеле.
                Тип данных: int
        """
        
        # маппинг классов с шаблонами и счетчиками
        self.label_mapping = {
            'отель': {
                'template': booking_template,
                'counter': booking_error_counter, 
                'prediction': []
            },
            'самолет': {
                'template': tickets_template,
                'counter': tickets_error_counter,
                'prediction': []
            }
        }

    def score(self):
        for label in ['самолет', 'отель']:
            print(f'Точность для класса "{label}"\n')
            for key, value in self.label_mapping[label]['counter'].items():
                print(f'\t{key}: {1-value/len(self.label_mapping[label]["prediction"]):.5f}\n')

    def count_errors(self, sample, prediction):
        fixed_json = fix_json(sample.json, prediction)
        for key in fixed_json.keys():
            if sample.json[key] != fixed_json[key]:
                self.label_mapping[sample.label]['counter'][key] += 1
        self.label_mapping[sample.label]['prediction'].append(fixed_json)