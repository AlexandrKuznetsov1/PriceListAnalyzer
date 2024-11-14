import csv
import os
import pandas as pd


class PriceMachine():

    def __init__(self):
        self.data = []
        self.result = ''
        self.data_res = []
        self.name_length = 0
        self.selection = pd.DataFrame(columns=['№', 'Наименование', 'Цена', 'Вес', 'Файл', 'Цена за кг.'])
    
    def load_prices(self, file_path=''):
        """
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт
                
            Допустимые названия для столбца с ценой:
                розница
                цена
                
            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        """
        valid_column_names = {
            'Название': ['товар', 'название', 'наименование', 'продукт'],
            'Цена': ['розница', 'цена'],
            'Вес': ['вес', 'масса', 'фасовка'],
        }
        for file in os.listdir(file_path):
            if 'price' in file and file.endswith('.csv'):
                with open(os.path.join(file_path, file), 'r', encoding='utf-8') as csvfile:
                    csv_read = csv.DictReader(csvfile, delimiter=',')
                    for row in csv_read:
                        data = {'Файл': file}
                        for key, variant_keys in valid_column_names.items():
                            for suitable_key in variant_keys:
                                if suitable_key in row:
                                    data[key] = row[suitable_key]
                        self.data.append(data)

    def _search_product_price_weight(self, headers):
        """
            Возвращает список словарей, где ключи - названия столбцов, значения - значения строк
        """
        self.columns = [product for product in self.data if headers.lower() in product.get('Название', '').lower()]
        self.sorted_results = sorted(self.columns, key=lambda x: float(x.get('цена', 0)) / float(x.get('вес', 1)))
        return self.sorted_results

    def export_to_html(self, df, fname='output.html'):
        """
        Из полученного датафрейма формирует HTML-файл и сохраняет его, о чем информирует пользователя
        :param df:
        :param fname:
        :return:
        """
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for i in range(len(df)):
            result += '<tr>'
            result += f'<td align="center"> {i+1}</td>'
            result += f'<td> {df["Наименование"].values[i]}</td>'
            result += f'<td align="center"> {df["Цена"].values[i]}</td>'
            result += f'<td align="center"> {df["Вес"].values[i]}</td>'
            result += f'<td> {df["Файл"].values[i]}</td>'
            result += f'<td align="center"> {df["Цена за кг."].values[i]}</td>'
            result += '</tr>\n'
        result += '\t</table>\n'
        result += '</body>'
        with open(fname, 'w') as f:
            f.write(result)
        print('Файл "output.html" успешно сохранен')
        pm.load_prices(r'prices')
    
    def find_text(self, text):
        """
        Обрабатывает запрос пользователя, формирует датафрейм по запросу,
        выводит датафрейм в консоль,
        передает датафрейм для формирования HTML-файла
        :param text:
        :return:
        """
        pm._search_product_price_weight(text)
        self.data_res.clear()
        for i, result in enumerate(self.sorted_results, 1):
            price_per_unit = round(int(result['Цена']) / float(result['Вес']), 2)
            result['Цена за килограмм'] = price_per_unit
            self.data_res.append(result.values())
        df = pd.DataFrame(self.data_res, columns=['Файл', 'Наименование', 'Цена', 'Вес', 'Цена за кг.'])
        take = df['Вес']
        df = df.drop('Вес', axis=1)
        df.insert(0, 'Вес', take)
        take = df['Цена']
        df = df.drop('Цена', axis=1)
        df.insert(0, 'Цена', take)
        take = df['Наименование']
        df = df.drop('Наименование', axis=1)
        df.insert(0, 'Наименование', take)
        sorted_df = df.sort_values(by='Цена за кг.')
        sorted_df.index = range(1, len(df) + 1)
        df = sorted_df.rename_axis('№', axis='index')
        try:
            if df.empty == True:
                raise RuntimeError('нет данных')
            print(df)
            pm.export_to_html(df)
        except Exception as e:
            print("Введены некорректные данные")

pm = PriceMachine()
pm.load_prices(r'prices')
"""
Логика работы программы
"""
while True:
    user_request = input("Введите фрагмент наименования товара для поиска (или 'exit' для выхода): ")
    if user_request == "exit":
        break
    pm.find_text(user_request)
print('the end')

