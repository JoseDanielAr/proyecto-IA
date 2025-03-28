from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a real secret key!

# Configuration
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

MODEL_PATH = "model.pt"

# Debugging: Check if model.pt exists
if not os.path.exists(MODEL_PATH):
    print("ERROR: model.pt not found!")

# Load model
model = YOLO('model.pt')

# Food name mapping
FOOD_MAPPING = {
    'almond': 'almendra',
    'apple': 'manzana',
    'asparagus': 'espárrago',
    'avocado': 'aguacate',
    'banana': 'plátano',
    'beef': 'carne de res',
    'beet': 'remolacha',
    'bell_pepper': 'pimiento',
    'blueberries': 'arándanos',
    'bread': 'pan',
    'broccoli': 'brócoli',
    'butter': 'mantequilla',
    'cabbage': 'col',
    'carrot': 'zanahoria',
    'cauliflower': 'coliflor',
    'celery': 'apio',
    'cheese': 'queso',
    'chicken': 'pollo',
    'chilli_pepper': 'chile picante',
    'chillies': 'chiles',
    'coriander': 'cilantro',
    'corn': 'maíz',
    'cucumber': 'pepino',
    'egg': 'huevo',
    'eggplant': 'berenjena',
    'fish': 'pescado',
    'flour': 'harina',
    'garlic': 'ajo',
    'ginger': 'jengibre',
    'grapes': 'uvas',
    'green beans': 'ejotes',
    'green_beans': 'ejotes',
    'green_onion': 'cebolla de verdeo',
    'jam': 'mermelada',
    'juice': 'jugo',
    'ketchup': 'salsa de tomate',
    'lemon': 'limón',
    'lettuce': 'lechuga',
    'lime': 'lima',
    'mango': 'mango',
    'mayonaise': 'mayonesa',
    'meat': 'carne',
    'milk': 'leche',
    'mushroom': 'hongo',
    'mushrooms': 'hongos',
    'mustard': 'mostaza',
    'oil': 'aceite',
    'olive': 'aceituna',
    'onion': 'cebolla',
    'orange': 'naranja',
    'pasta': 'pasta',
    'peanut_butter': 'mantequilla de maní',
    'pear': 'pera',
    'peas': 'guisantes',
    'pineapple': 'piña',
    'plum': 'ciruela',
    'pork': 'carne de cerdo',
    'potato': 'papa',
    'pumpkin': 'calabaza',
    'radish': 'rábano',
    'rice': 'arroz',
    'salmon': 'salmón',
    'shrimp': 'camarón',
    'soysauce': 'salsa de soya',
    'spinach': 'espinaca',
    'strawberry': 'fresa',
    'sugar': 'azúcar',
    'sweet_potato': 'batata',
    'tomato': 'tomate',
    'tomato_sauce': 'salsa de tomate',
    'watermelon': 'sandía',
    'yogurt': 'yogur'
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Recipe database (add your own recipes here)
RECIPE_DATABASE = [
    {
        'name': 'Ensalada de Almendras y Espinaca',
        'ingredients': ['almendra', 'espinaca'],
        'description': 'Ensalada crujiente y saludable con almendras y espinaca.',
        'steps': [
            'Lavar bien las hojas de espinaca.',
            'Tostar las almendras en una sartén sin aceite.',
            'Mezclar todo y añadir aceite de oliva y sal al gusto.'
        ]
    },
    {
        'name': 'Batido de Plátano y Leche',
        'ingredients': ['plátano', 'leche'],
        'description': 'Un batido cremoso y energético.',
        'steps': [
            'Pelar y cortar el plátano en trozos.',
            'Colocar en una licuadora con la leche.',
            'Licuar hasta obtener una mezcla homogénea y servir.'
        ]
    },
    {
        'name': 'Ensalada Mediterránea',
        'ingredients': ['tomate', 'pepino'],
        'description': 'Ensalada fresca estilo mediterráneo',
        'steps': [
            'Cortar tomates y pepinos',
            'Mezclar con aceite de oliva',
            'Añadir sal al gusto'
        ]
    },
    {
        'name': 'Puré de Papa y Ajo',
        'ingredients': ['papa', 'ajo'],
        'description': 'Puré suave con un toque de ajo.',
        'steps': [
            'Hervir las papas hasta que estén blandas.',
            'Machacar con un tenedor y añadir ajo picado.',
            'Mezclar con mantequilla y un poco de leche hasta lograr la textura deseada.'
        ]
    },
    {
        'name': 'Salmón al Limón',
        'ingredients': ['salmón', 'limón'],
        'description': 'Salmón jugoso con un toque cítrico.',
        'steps': [
            'Colocar el salmón en una bandeja para horno.',
            'Exprimir el limón sobre el salmón.',
            'Hornear a 180°C durante 20 minutos.'
        ]
    },
    {
        'name': 'Sopa de Hongos',
        'ingredients': ['hongo', 'leche'],
        'description': 'Sopa cremosa de hongos.',
        'steps': [
            'Saltear los hongos en una sartén con aceite.',
            'Añadir leche y cocinar a fuego lento.',
            'Licuar la mezcla hasta obtener una crema suave.'
        ]
    },
    {
        'name': 'Arroz con Maíz',
        'ingredients': ['arroz', 'maíz'],
        'description': 'Un plato sencillo pero delicioso.',
        'steps': [
            'Cocinar el arroz en agua hirviendo.',
            'Añadir maíz y mezclar bien.',
            'Servir caliente con un poco de mantequilla.'
        ]
    },
    {
        'name': 'Tostada con Mantequilla de Maní y Mermelada',
        'ingredients': ['pan', 'mantequilla de maní', 'mermelada'],
        'description': 'Un desayuno clásico y delicioso.',
        'steps': [
            'Tostar una rebanada de pan.',
            'Untar mantequilla de maní y luego mermelada.',
            'Servir con un vaso de leche o jugo.'
        ]
    },
    {
        'name': 'Ensalada de Lechuga y Pepino',
        'ingredients': ['lechuga', 'pepino'],
        'description': 'Ensalada fresca y ligera.',
        'steps': [
            'Lavar y cortar la lechuga y el pepino.',
            'Mezclar en un tazón y añadir aceite de oliva.',
            'Servir con una pizca de sal al gusto.'
        ]
    },
    {
        'name': 'Pasta con Salsa de Tomate',
        'ingredients': ['pasta', 'salsa de tomate'],
        'description': 'Pasta clásica con una salsa de tomate casera.',
        'steps': [
            'Cocinar la pasta en agua hirviendo.',
            'Calentar la salsa de tomate en una sartén.',
            'Mezclar la pasta con la salsa y servir caliente.'
        ]
    },
    {
        'name': 'Batido de Fresa y Yogur',
        'ingredients': ['fresa', 'yogur'],
        'description': 'Un batido refrescante y nutritivo.',
        'steps': [
            'Lavar y cortar las fresas.',
            'Mezclar con yogur en una licuadora.',
            'Servir frío y disfrutar.'
        ]
    },
    {
        'name': 'Batido de Arándanos y Jugo de Naranja',
        'ingredients': ['arándanos', 'jugo', 'naranja'],
        'description': 'Un batido antioxidante y refrescante.',
        'steps': [
            'Lavar los arándanos y colocarlos en una licuadora.',
            'Añadir jugo de naranja y licuar hasta obtener una mezcla homogénea.',
            'Servir frío y disfrutar.'
        ]
    },
    {
        'name': 'Sándwich de Queso y Jamón',
        'ingredients': ['pan', 'queso'],
        'description': 'Un sándwich sencillo pero delicioso.',
        'steps': [
            'Colocar una rebanada de queso entre dos rebanadas de pan.',
            'Calentar en una sartén hasta que el queso se derrita.',
            'Servir caliente.'
        ]
    },
    {
        'name': 'Pimientos Rellenos de Carne de Res',
        'ingredients': ['pimiento', 'carne de res'],
        'description': 'Pimientos rellenos con un toque jugoso.',
        'steps': [
            'Cortar la parte superior de los pimientos y retirar las semillas.',
            'Rellenar con carne de res cocida y condimentada.',
            'Hornear a 180°C durante 25 minutos.'
        ]
    },
    {
        'name': 'Calabaza Asada con Miel',
        'ingredients': ['calabaza', 'azúcar'],
        'description': 'Un postre dulce y natural.',
        'steps': [
            'Cortar la calabaza en trozos medianos.',
            'Espolvorear con azúcar y hornear a 200°C durante 30 minutos.',
            'Servir caliente.'
        ]
    },
    {
        'name': 'Pollo al Ajo con Arroz',
        'ingredients': ['pollo', 'ajo', 'arroz'],
        'description': 'Un plato sustancioso con mucho sabor.',
        'steps': [
            'Dorar el pollo en una sartén con ajo picado.',
            'Cocinar el arroz y servirlo como acompañamiento.',
            'Disfrutar caliente.'
        ]
    },
    {
        'name': 'Camarones con Salsa de Soja y Limón',
        'ingredients': ['camarón', 'salsa de soya', 'limón'],
        'description': 'Un plato rápido y lleno de sabor asiático.',
        'steps': [
            'Saltear los camarones en una sartén.',
            'Añadir salsa de soya y jugo de limón.',
            'Servir caliente con arroz o verduras.'
        ]
    },
    {
        'name': 'Puré de Batata con Mantequilla',
        'ingredients': ['batata', 'mantequilla'],
        'description': 'Un puré suave y dulce.',
        'steps': [
            'Hervir las batatas hasta que estén blandas.',
            'Machacar y mezclar con mantequilla.',
            'Servir caliente como acompañamiento.'
        ]
    },
    {
        'name': 'Pera al Horno con Canela',
        'ingredients': ['pera', 'azúcar'],
        'description': 'Un postre simple y aromático.',
        'steps': [
            'Cortar las peras por la mitad y espolvorear con azúcar.',
            'Hornear a 180°C durante 20 minutos.',
            'Servir caliente o frío.'
        ]
    },
    {
        'name': 'Guisantes con Zanahoria y Mantequilla',
        'ingredients': ['guisantes', 'zanahoria', 'mantequilla'],
        'description': 'Un acompañamiento colorido y nutritivo.',
        'steps': [
            'Cocer los guisantes y las zanahorias en agua hirviendo.',
            'Escurrir y mezclar con mantequilla derretida.',
            'Servir caliente.'
        ]
    },
    {
        'name': 'Tacos de Cerdo con Cebolla y Cilantro',
        'ingredients': ['carne de cerdo', 'cebolla', 'cilantro'],
        'description': 'Tacos con un sabor tradicional.',
        'steps': [
            'Cocinar la carne de cerdo hasta que esté dorada.',
            'Picar la cebolla y el cilantro.',
            'Servir en tortillas con los ingredientes frescos por encima.'
        ]
    },
    {
        'name': 'Brócoli Salteado con Ajo y Aceite de Oliva',
        'ingredients': ['brócoli', 'ajo', 'aceite'],
        'description': 'Un plato sencillo y saludable.',
        'steps': [
            'Cortar el brócoli en trozos pequeños.',
            'Saltear en una sartén con ajo picado y un poco de aceite.',
            'Servir caliente como acompañamiento.'
        ]
    },
    {
        'name': 'Ensalada de Pepino y Cebolla de Verdeo',
        'ingredients': ['pepino', 'cebolla de verdeo'],
        'description': 'Ensalada fresca y crujiente.',
        'steps': [
            'Cortar el pepino y la cebolla de verdeo en rodajas finas.',
            'Mezclar en un bol y aliñar con sal y jugo de limón.',
            'Servir frío.'
        ]
    },
    {
        'name': 'Tortilla de Espinaca y Champiñones',
        'ingredients': ['espinaca', 'hongo', 'huevo'],
        'description': 'Una tortilla ligera y nutritiva.',
        'steps': [
            'Batir los huevos y añadir la espinaca y los hongos picados.',
            'Cocinar en una sartén con un poco de aceite.',
            'Servir caliente.'
        ]
    },
    {
        'name': 'Papas al Horno con Mostaza',
        'ingredients': ['papa', 'mostaza'],
        'description': 'Papas doradas con un toque de mostaza.',
        'steps': [
            'Cortar las papas en trozos medianos.',
            'Mezclar con mostaza y hornear a 200°C durante 30 minutos.',
            'Servir caliente.'
        ]
    },
    {
        'name': 'Sándwich de Jamón, Queso y Mayonesa',
        'ingredients': ['pan', 'queso', 'mayonesa'],
        'description': 'Un sándwich cremoso y delicioso.',
        'steps': [
            'Untar mayonesa en una rebanada de pan.',
            'Colocar una rebanada de queso y cerrar el sándwich.',
            'Servir frío o calentar en una sartén.'
        ]
    },
    {
        'name': 'Batido de Mango y Yogur',
        'ingredients': ['mango', 'yogur'],
        'description': 'Un batido tropical y refrescante.',
        'steps': [
            'Pelar y cortar el mango en trozos.',
            'Mezclar con yogur en una licuadora.',
            'Servir frío y disfrutar.'
        ]
    },
    {
        'name': 'Puré de Zanahoria con Jengibre',
        'ingredients': ['zanahoria', 'jengibre'],
        'description': 'Puré con un toque especial de jengibre.',
        'steps': [
            'Hervir las zanahorias hasta que estén blandas.',
            'Machacar y mezclar con jengibre rallado.',
            'Servir caliente.'
        ]
    },
    {
        'name': 'Ensalada de Repollo y Zanahoria',
        'ingredients': ['col', 'zanahoria'],
        'description': 'Ensalada crujiente y fresca.',
        'steps': [
            'Rallar la col y la zanahoria en tiras finas.',
            'Mezclar en un tazón y aliñar con aceite y limón.',
            'Servir fría.'
        ]
    },
    {
        'name': 'Tostadas con Aceitunas y Queso',
        'ingredients': ['pan', 'aceituna', 'queso'],
        'description': 'Un aperitivo simple y sabroso.',
        'steps': [
            'Tostar una rebanada de pan.',
            'Colocar aceitunas picadas y queso encima.',
            'Hornear unos minutos y servir.'
        ]
    },
    {
        'name': 'Pollo al Ketchup con Arroz',
        'ingredients': ['pollo', 'ketchup', 'arroz'],
        'description': 'Pollo jugoso con un toque dulce.',
        'steps': [
            'Cocinar el pollo en una sartén.',
            'Añadir ketchup y mezclar bien.',
            'Servir con arroz caliente.'
        ]
    },
    {
        'name': 'Sopa de Cebolla',
        'ingredients': ['cebolla', 'mantequilla'],
        'description': 'Sopa caliente con un sabor suave y delicioso.',
        'steps': [
            'Cortar la cebolla en rodajas finas.',
            'Saltear en mantequilla hasta que esté dorada.',
            'Añadir agua y cocinar a fuego lento por 20 minutos.'
        ]
    },
    {
        'name': 'Berenjena Asada con Ajo y Aceite de Oliva',
        'ingredients': ['berenjena', 'ajo', 'aceite'],
        'description': 'Un plato simple y lleno de sabor.',
        'steps': [
            'Cortar la berenjena en rodajas.',
            'Pintar con aceite de oliva y ajo picado.',
            'Hornear a 200°C por 25 minutos.'
        ]
    },
    {
        'name': 'Hamburguesa de Carne de Res con Mostaza',
        'ingredients': ['carne de res', 'mostaza', 'pan'],
        'description': 'Una hamburguesa con un toque especial.',
        'steps': [
            'Formar hamburguesas con la carne de res.',
            'Cocinar en una sartén y untar mostaza sobre el pan.',
            'Colocar la hamburguesa en el pan y servir.'
        ]
    },
    {
        'name': 'Ensalada de Rábanos y Cilantro',
        'ingredients': ['rábano', 'cilantro'],
        'description': 'Ensalada fresca y ligeramente picante.',
        'steps': [
            'Cortar los rábanos en rodajas finas.',
            'Picar el cilantro y mezclar con los rábanos.',
            'Aliñar con limón y aceite de oliva.'
        ]
    },
    {
        'name': 'Plátano con Miel y Canela',
        'ingredients': ['plátano', 'azúcar'],
        'description': 'Postre dulce y natural.',
        'steps': [
            'Cortar el plátano en rodajas.',
            'Espolvorear con azúcar y canela.',
            'Servir frío o calentar unos segundos en el microondas.'
        ]
    },
    {
        'name': 'Galletas de Harina y Mantequilla',
        'ingredients': ['harina', 'mantequilla', 'azúcar'],
        'description': 'Galletas caseras y crujientes.',
        'steps': [
            'Mezclar la harina con mantequilla y azúcar.',
            'Formar pequeñas galletas y hornear a 180°C durante 15 minutos.',
            'Dejar enfriar y servir.'
        ]
    },
    {
        'name': 'Papas con Chiles y Limón',
        'ingredients': ['papa', 'chiles', 'limón'],
        'description': 'Papas picantes con un toque cítrico.',
        'steps': [
            'Cortar las papas en cubos y freír hasta dorar.',
            'Mezclar con chiles picados y jugo de limón.',
            'Servir caliente.'
        ]
    },
    {
        'name': 'Piña Asada con Azúcar',
        'ingredients': ['piña', 'azúcar'],
        'description': 'Un postre tropical y caramelizado.',
        'steps': [
            'Cortar la piña en rodajas.',
            'Espolvorear con azúcar y asar en una sartén.',
            'Servir caliente con un toque de canela si se desea.'
        ]
    },
    {
        'name': 'Sopa de Calabaza y Leche',
        'ingredients': ['calabaza', 'leche'],
        'description': 'Sopa cremosa y reconfortante.',
        'steps': [
            'Cocer la calabaza hasta que esté blanda.',
            'Licuar con leche hasta obtener una crema.',
            'Calentar y servir con un poco de sal.'
        ]
    },
    {
        'name': 'Pasta con Aceitunas y Queso',
        'ingredients': ['pasta', 'aceituna', 'queso'],
        'description': 'Un plato rápido y delicioso.',
        'steps': [
            'Cocer la pasta en agua hirviendo.',
            'Añadir aceitunas picadas y queso rallado.',
            'Mezclar y servir caliente.'
        ]
    },
    {
        'name': 'Ensalada de Maíz y Pepino',
        'ingredients': ['maíz', 'pepino'],
        'description': 'Ensalada fresca y dulce.',
        'steps': [
            'Cortar el pepino en rodajas finas.',
            'Mezclar con el maíz en un bol.',
            'Aliñar con jugo de limón y sal.'
        ]
    },
    {
        'name': 'Guiso de Lentejas con Zanahoria y Ajo',
        'ingredients': ['zanahoria', 'ajo'],
        'description': 'Un guiso nutritivo y reconfortante.',
        'steps': [
            'Cortar la zanahoria en cubos pequeños.',
            'Sofreír con ajo picado y añadir agua.',
            'Cocinar hasta que las zanahorias estén tiernas y servir caliente.'
        ]
    },
    {
        'name': 'Batido de Plátano con Mantequilla de Maní',
        'ingredients': ['plátano', 'mantequilla de maní', 'leche'],
        'description': 'Batido cremoso y energético.',
        'steps': [
            'Colocar el plátano en la licuadora.',
            'Añadir mantequilla de maní y leche.',
            'Licuar hasta obtener una mezcla homogénea y servir.'
        ]
    },
    {
        'name': 'Salmón al Horno con Limón',
        'ingredients': ['salmón', 'limón'],
        'description': 'Salmón jugoso con un toque cítrico.',
        'steps': [
            'Colocar el salmón en una bandeja para hornear.',
            'Rociar con jugo de limón y hornear a 180°C por 20 minutos.',
            'Servir caliente con una guarnición de ensalada.'
        ]
    },
    {
        'name': 'Ensalada de Piña y Pepino',
        'ingredients': ['piña', 'pepino'],
        'description': 'Ensalada refrescante con un toque tropical.',
        'steps': [
            'Cortar la piña y el pepino en cubos.',
            'Mezclar en un bol y refrigerar por 10 minutos.',
            'Servir fría como acompañamiento.'
        ]
    },
    {
        'name': 'Huevos Revueltos con Espinaca',
        'ingredients': ['huevo', 'espinaca'],
        'description': 'Un desayuno saludable y fácil de preparar.',
        'steps': [
            'Batir los huevos en un tazón.',
            'Saltear la espinaca en una sartén y añadir los huevos.',
            'Cocinar hasta que los huevos estén listos y servir caliente.'
        ]
    },
    {
        'name': 'Puré de Papa con Mantequilla',
        'ingredients': ['papa', 'mantequilla'],
        'description': 'Puré cremoso y suave.',
        'steps': [
            'Hervir las papas hasta que estén blandas.',
            'Machacar y mezclar con mantequilla.',
            'Servir caliente como acompañamiento.'
        ]
    },
    {
        'name': 'Tostadas con Mermelada de Fresas',
        'ingredients': ['pan', 'mermelada'],
        'description': 'Un desayuno dulce y clásico.',
        'steps': [
            'Tostar una rebanada de pan.',
            'Untar con mermelada de fresas.',
            'Servir con café o leche.'
        ]
    },
    {
        'name': 'Pimientos Salteados con Ajo',
        'ingredients': ['pimiento', 'ajo'],
        'description': 'Un acompañamiento ligero y sabroso.',
        'steps': [
            'Cortar los pimientos en tiras finas.',
            'Saltear en una sartén con ajo picado.',
            'Servir caliente como guarnición.'
        ]
    },
    {
        'name': 'Jugo de Naranja con Jengibre',
        'ingredients': ['jugo', 'naranja', 'jengibre'],
        'description': 'Bebida refrescante con un toque picante.',
        'steps': [
            'Exprimir el jugo de naranja.',
            'Añadir jengibre rallado y mezclar bien.',
            'Servir frío con hielo.'
        ]
    },
    {
        'name': 'Ensalada de Uvas y Queso',
        'ingredients': ['uvas', 'queso'],
        'description': 'Una ensalada fresca y dulce.',
        'steps': [
            'Cortar las uvas por la mitad.',
            'Mezclar con queso en cubos.',
            'Servir frío con un toque de miel opcional.'
        ]
    },
    {
        'name': 'Pasta con Salsa de Tomate',
        'ingredients': ['pasta', 'salsa de tomate'],
        'description': 'Un plato clásico y delicioso.',
        'steps': [
            'Cocinar la pasta en agua hirviendo.',
            'Calentar la salsa de tomate en una sartén.',
            'Mezclar la pasta con la salsa y servir caliente.'
        ]
    },
    {
        'name': 'Batido de Piña y Yogur',
        'ingredients': ['piña', 'yogur'],
        'description': 'Un batido tropical y refrescante.',
        'steps': [
            'Cortar la piña en trozos pequeños.',
            'Licuar con yogur hasta obtener una mezcla cremosa.',
            'Servir frío con hielo.'
        ]
    },
    {
        'name': 'Pechuga de Pollo al Ajo',
        'ingredients': ['pollo', 'ajo'],
        'description': 'Un plato jugoso y lleno de sabor.',
        'steps': [
            'Salpimentar la pechuga de pollo.',
            'Cocinar en una sartén con ajo picado.',
            'Servir caliente con una guarnición de ensalada.'
        ]
    },
    {
        'name': 'Arroz con Champiñones',
        'ingredients': ['arroz', 'hongo'],
        'description': 'Un acompañamiento sabroso y sencillo.',
        'steps': [
            'Cocinar el arroz en agua con sal.',
            'Saltear los champiñones en una sartén.',
            'Mezclar con el arroz y servir caliente.'
        ]
    },
    {
        'name': 'Sándwich de Atún con Mayonesa',
        'ingredients': ['pan', 'pescado', 'mayonesa'],
        'description': 'Un sándwich fácil y delicioso.',
        'steps': [
            'Mezclar el pescado desmenuzado con mayonesa.',
            'Colocar sobre una rebanada de pan.',
            'Cubrir con otra rebanada y servir.'
        ]
    },
    {
        'name': 'Salmón con Salsa de Soya',
        'ingredients': ['salmón', 'salsa de soya'],
        'description': 'Un plato con un toque asiático.',
        'steps': [
            'Cocinar el salmón a la plancha.',
            'Rociar con salsa de soya y dejar reposar.',
            'Servir caliente con arroz o ensalada.'
        ]
    },
    {
        'name': 'Cebolla de Verdeo Salteada',
        'ingredients': ['cebolla de verdeo', 'aceite'],
        'description': 'Un acompañamiento ligero y sabroso.',
        'steps': [
            'Cortar la cebolla de verdeo en rodajas.',
            'Saltear en aceite caliente por unos minutos.',
            'Servir como guarnición.'
        ]
    },
    {
        'name': 'Pan con Mermelada de Uva',
        'ingredients': ['pan', 'mermelada', 'uvas'],
        'description': 'Un desayuno dulce y rápido.',
        'steps': [
            'Tostar una rebanada de pan.',
            'Untar con mermelada y colocar uvas partidas encima.',
            'Servir con café o leche.'
        ]
    },
    {
        'name': 'Batido de Fresas con Leche',
        'ingredients': ['fresa', 'leche'],
        'description': 'Bebida refrescante y cremosa.',
        'steps': [
            'Lavar y cortar las fresas.',
            'Licuar con leche hasta obtener una mezcla homogénea.',
            'Servir frío con hielo.'
        ]
    },
    {
        'name': 'Papas con Salsa de Queso',
        'ingredients': ['papa', 'queso'],
        'description': 'Papas cremosas y deliciosas.',
        'steps': [
            'Hervir las papas hasta que estén tiernas.',
            'Derretir queso en una sartén con un poco de leche.',
            'Cubrir las papas con la salsa y servir.'
        ]
    },
    {
        'name': 'Tostadas con Aceite de Oliva y Ajo',
        'ingredients': ['pan', 'aceite', 'ajo'],
        'description': 'Un aperitivo crujiente y aromático.',
        'steps': [
            'Tostar el pan en una sartén.',
            'Frotar con ajo y rociar con aceite de oliva.',
            'Servir caliente.'
        ]
    },
    {
        'name': 'Ensalada de Lechuga con Limón',
        'ingredients': ['lechuga', 'limón'],
        'description': 'Una ensalada ligera y saludable.',
        'steps': [
            'Lavar y cortar la lechuga en trozos.',
            'Aliñar con jugo de limón y una pizca de sal.',
            'Servir como acompañamiento.'
        ]
    },
    {
        'name': 'Arroz con Zanahoria y Chiles',
        'ingredients': ['arroz', 'zanahoria', 'chiles'],
        'description': 'Un arroz con un toque de picante.',
        'steps': [
            'Cocinar el arroz en agua con sal.',
            'Saltear zanahorias y chiles en una sartén.',
            'Mezclar con el arroz y servir caliente.'
        ]
    },
    {
        'name': 'Galletas de Harina y Azúcar',
        'ingredients': ['harina', 'azúcar'],
        'description': 'Galletas dulces y fáciles de hacer.',
        'steps': [
            'Mezclar la harina con azúcar y un poco de agua.',
            'Formar bolitas y hornear a 180°C por 15 minutos.',
            'Dejar enfriar y servir.'
        ]
    },
    {
        'name': 'Pepinos con Salsa de Yogur',
        'ingredients': ['pepino', 'yogur'],
        'description': 'Un acompañamiento refrescante.',
        'steps': [
            'Cortar los pepinos en rodajas.',
            'Mezclar con yogur y una pizca de sal.',
            'Servir frío como aperitivo o guarnición.'
        ]
    },
    {
        'name': 'Jugo de Naranja con Miel',
        'ingredients': ['jugo', 'naranja', 'azúcar'],
        'description': 'Bebida dulce y natural.',
        'steps': [
            'Exprimir el jugo de naranja.',
            'Añadir azúcar al gusto y mezclar bien.',
            'Servir frío con hielo.'
        ]
    },
    {
        'name': 'Batido de Mango con Yogur',
        'ingredients': ['mango', 'yogur'],
        'description': 'Un batido tropical y nutritivo.',
        'steps': [
            'Cortar el mango en trozos pequeños.',
            'Licuar con yogur hasta obtener una textura cremosa.',
            'Servir frío y disfrutar.'
        ]
    },
    {
        'name': 'Verduras Salteadas con Salsa de Soya',
        'ingredients': ['brócoli', 'pimiento', 'salsa de soya'],
        'description': 'Un platillo ligero y sabroso.',
        'steps': [
            'Cortar el brócoli y los pimientos en trozos pequeños.',
            'Saltear en una sartén con salsa de soya.',
            'Servir caliente como acompañamiento.'
        ]
    },
    {
        'name': 'Tostadas de Aguacate con Queso',
        'ingredients': ['pan', 'aguacate', 'queso'],
        'description': 'Tostadas crujientes con aguacate cremoso y queso.',
        'steps': [
            'Tostar el pan hasta que esté dorado.',
            'Machacar el aguacate y untarlo sobre el pan.',
            'Espolvorear queso rallado por encima y servir.'
        ]
    },
    {
        'name': 'Ensalada de Aguacate y Tomate',
        'ingredients': ['aguacate', 'tomate', 'cebolla', 'limón'],
        'description': 'Ensalada fresca con un toque cítrico.',
        'steps': [
            'Cortar el aguacate, el tomate y la cebolla en trozos pequeños.',
            'Mezclar en un bol y rociar con jugo de limón.',
            'Revolver bien y servir frío.'
        ]
    },
    {
        'name': 'Batido de Aguacate y Leche',
        'ingredients': ['aguacate', 'leche', 'azúcar'],
        'description': 'Un batido cremoso y nutritivo.',
        'steps': [
            'Pelar y cortar el aguacate en trozos.',
            'Licuar con leche y azúcar hasta obtener una mezcla homogénea.',
            'Servir frío con hielo opcional.'
        ]
    },
    {
        'name': 'Ensalada de Apio y Manzana',
        'ingredients': ['apio', 'manzana', 'mayonesa'],
        'description': 'Una ensalada fresca y crujiente con un toque cremoso.',
        'steps': [
            'Cortar el apio y la manzana en trozos pequeños.',
            'Mezclar en un bol y añadir mayonesa.',
            'Revolver bien y servir frío.'
        ]
    },
    {
        'name': 'Sopa de Apio y Zanahoria',
        'ingredients': ['apio', 'zanahoria', 'cebolla'],
        'description': 'Una sopa reconfortante y nutritiva.',
        'steps': [
            'Picar el apio, la zanahoria y la cebolla.',
            'Saltear en una olla con un poco de aceite.',
            'Añadir agua, cocinar hasta que las verduras estén tiernas y servir caliente.'
        ]
    },
    {
        'name': 'Jugo Verde de Apio y Limón',
        'ingredients': ['apio', 'limón', 'jugo'],
        'description': 'Un jugo refrescante y desintoxicante.',
        'steps': [
            'Picar el apio en trozos pequeños.',
            'Exprimir el limón y mezclar con el apio en la licuadora.',
            'Añadir un poco de jugo de naranja y servir frío.'
        ]
    },
    {
        'name': 'Tacos de Carne con Cebolla y Cilantro',
        'ingredients': ['carne', 'cebolla', 'cilantro'],
        'description': 'Tacos mexicanos con carne jugosa y un toque fresco de cilantro.',
        'steps': [
            'Cortar la carne en trozos pequeños y cocinar en una sartén con un poco de aceite.',
            'Picar la cebolla y el cilantro finamente.',
            'Servir la carne en tortillas y añadir la cebolla y el cilantro por encima.'
        ]
    },
    {
        'name': 'Estofado de Carne con Zanahoria y Papa',
        'ingredients': ['carne', 'zanahoria', 'papa', 'cebolla'],
        'description': 'Un estofado casero, reconfortante y lleno de sabor.',
        'steps': [
            'Cortar la carne en trozos medianos y dorar en una olla con un poco de aceite.',
            'Añadir la cebolla picada y cocinar hasta que esté transparente.',
            'Agregar la zanahoria y la papa en trozos, cubrir con agua y cocinar a fuego lento hasta que todo esté tierno.'
        ]
    },
    {
        'name': 'Carne Salteada con Pimientos',
        'ingredients': ['carne', 'pimiento', 'ajo', 'salsa de soya'],
        'description': 'Un platillo salteado con un toque asiático.',
        'steps': [
            'Cortar la carne y los pimientos en tiras finas.',
            'Saltear la carne en una sartén con ajo picado.',
            'Añadir los pimientos y la salsa de soya, cocinar unos minutos más y servir caliente.'
        ]
    },
    {
        'name': 'Salsa Picante de Tomate y Chile',
        'ingredients': ['tomate', 'chile picante', 'ajo'],
        'description': 'Una salsa casera con un toque de picante perfecta para acompañar cualquier platillo.',
        'steps': [
            'Asar los tomates y el chile picante en un sartén.',
            'Licuar con ajo y sal hasta obtener una salsa homogénea.',
            'Servir con tacos, carne o nachos.'
        ]
    },
    {
        'name': 'Sopa Picante de Pollo y Verduras',
        'ingredients': ['pollo', 'chile picante', 'zanahoria', 'cebolla'],
        'description': 'Una sopa caliente con el picante perfecto para despertar el paladar.',
        'steps': [
            'Cocer el pollo en agua con sal hasta que esté tierno.',
            'Añadir zanahoria y cebolla picada a la olla.',
            'Agregar chile picante picado y cocinar unos minutos más antes de servir.'
        ]
    },
    {
        'name': 'Salteado de Camarón con Chile Picante y Ajo',
        'ingredients': ['camarón', 'chile picante', 'ajo', 'limón'],
        'description': 'Un platillo lleno de sabor con el toque picante del chile y el frescor del limón.',
        'steps': [
            'Saltear los camarones en una sartén con ajo picado.',
            'Añadir chile picante en rodajas y cocinar unos minutos más.',
            'Exprimir jugo de limón por encima y servir caliente.'
        ]
    },
    {
        'name': 'Mermelada de Ciruela Casera',
        'ingredients': ['ciruela', 'azúcar', 'limón'],
        'description': 'Una mermelada dulce y ácida perfecta para el desayuno.',
        'steps': [
            'Cortar las ciruelas en trozos pequeños y retirar los huesos.',
            'Cocinarlas en una olla con azúcar y jugo de limón a fuego bajo.',
            'Dejar enfriar y guardar en frascos para disfrutar en pan o postres.'
        ]
    },
    {
        'name': 'Ensalada de Ciruela y Espinaca',
        'ingredients': ['ciruela', 'espinaca', 'queso', 'nueces'],
        'description': 'Una ensalada fresca con el dulzor de la ciruela y el toque cremoso del queso.',
        'steps': [
            'Lavar y cortar las ciruelas en rodajas.',
            'Mezclar con espinaca fresca y queso desmenuzado.',
            'Añadir nueces y aliñar con aceite de oliva.'
        ]
    },
    {
        'name': 'Salsa de Ciruela para Carne',
        'ingredients': ['ciruela', 'ajo', 'salsa de soya'],
        'description': 'Una salsa agridulce perfecta para acompañar carnes.',
        'steps': [
            'Cortar las ciruelas y cocinarlas en una sartén con ajo picado.',
            'Añadir salsa de soya y dejar reducir hasta obtener una consistencia espesa.',
            'Servir caliente sobre carne a la parrilla o pollo.'
        ]
    },
    {
        'name': 'Coliflor Rostizada con Ajo y Limón',
        'ingredients': ['coliflor', 'ajo', 'limón', 'aceite'],
        'description': 'Una guarnición crujiente y llena de sabor.',
        'steps': [
            'Cortar la coliflor en floretes y mezclarlos con ajo picado, jugo de limón y aceite.',
            'Extender en una bandeja y hornear a 200°C por 25 minutos.',
            'Servir caliente con un toque extra de limón.'
        ]
    },
    {
        'name': 'Arroz de Coliflor con Cilantro',
        'ingredients': ['coliflor', 'cilantro', 'ajo', 'aceite'],
        'description': 'Una alternativa ligera al arroz tradicional con un toque fresco.',
        'steps': [
            'Rallar la coliflor hasta obtener una textura similar al arroz.',
            'Saltear en una sartén con un poco de aceite y ajo picado.',
            'Añadir cilantro picado y mezclar bien antes de servir.'
        ]
    },
    {
        'name': 'Coliflor en Salsa de Tomate',
        'ingredients': ['coliflor', 'salsa de tomate', 'queso'],
        'description': 'Coliflor bañada en salsa de tomate con un toque gratinado.',
        'steps': [
            'Cocer la coliflor en agua con sal hasta que esté tierna.',
            'Cubrir con salsa de tomate y espolvorear queso por encima.',
            'Hornear a 180°C hasta que el queso esté dorado.'
        ]
    },
    {
        'name': 'Ejotes Salteados con Ajo y Limón',
        'ingredients': ['ejotes', 'ajo', 'limón', 'aceite'],
        'description': 'Ejotes tiernos y crujientes con un toque cítrico.',
        'steps': [
            'Lavar y cortar los extremos de los ejotes.',
            'Saltear en una sartén con aceite y ajo picado hasta que estén tiernos.',
            'Añadir jugo de limón al gusto y servir caliente.'
        ]
    },
    {
        'name': 'Ensalada de Ejotes con Tomate y Queso',
        'ingredients': ['ejotes', 'tomate', 'queso', 'aceite'],
        'description': 'Ensalada fresca y ligera con el sabor de los ejotes y el tomate.',
        'steps': [
            'Cocer los ejotes en agua con sal hasta que estén tiernos.',
            'Cortar los tomates en cubos y mezclar con los ejotes cocidos.',
            'Añadir queso desmenuzado y aliñar con aceite antes de servir.'
        ]
    },
    {
        'name': 'Ejotes con Salsa de Tomate y Cebolla',
        'ingredients': ['ejotes', 'salsa de tomate', 'cebolla', 'ajo'],
        'description': 'Un platillo casero con ejotes bañados en salsa de tomate.',
        'steps': [
            'Cocer los ejotes en agua con sal y reservar.',
            'En una sartén, saltear la cebolla y el ajo picado hasta que estén dorados.',
            'Añadir la salsa de tomate y los ejotes, cocinar por unos minutos y servir caliente.'
        ]
    },
    {
        'name': 'Espárragos a la Parrilla con Limón y Ajo',
        'ingredients': ['espárrago', 'ajo', 'limón', 'aceite'],
        'description': 'Espárragos asados con un toque de ajo y limón.',
        'steps': [
            'Lavar los espárragos y cortar la parte dura del tallo.',
            'Mezclar con aceite, ajo picado y jugo de limón.',
            'Asar en una parrilla caliente por 5 minutos y servir caliente.'
        ]
    },
    {
        'name': 'Ensalada de Espárragos con Tomate y Queso',
        'ingredients': ['espárrago', 'tomate', 'queso', 'aceite'],
        'description': 'Una ensalada fresca con espárragos crujientes y queso cremoso.',
        'steps': [
            'Cocer los espárragos en agua con sal por 3 minutos y enfriar.',
            'Cortar los tomates en cubos y mezclar con los espárragos.',
            'Añadir queso desmenuzado y aliñar con aceite antes de servir.'
        ]
    },
    {
        'name': 'Espárragos Salteados con Champiñones y Ajo',
        'ingredients': ['espárrago', 'hongo', 'ajo', 'aceite'],
        'description': 'Un salteado rápido y sabroso con espárragos y champiñones.',
        'steps': [
            'Cortar los espárragos en trozos y los hongos en láminas.',
            'Saltear en una sartén con aceite y ajo picado hasta que estén dorados.',
            'Servir caliente como guarnición o plato principal.'
        ]
    },
    {
        'name': 'Aderezo de Lima y Cilantro',
        'ingredients': ['lima', 'cilantro', 'ajo', 'aceite'],
        'description': 'Un aderezo cítrico y fresco para ensaladas o carnes.',
        'steps': [
            'Exprimir el jugo de lima en un tazón.',
            'Añadir cilantro picado, ajo triturado y un poco de aceite.',
            'Mezclar bien y servir sobre ensaladas o carnes a la parrilla.'
        ]
    },
    {
        'name': 'Agua Fresca de Lima',
        'ingredients': ['lima', 'azúcar', 'jugo'],
        'description': 'Una bebida refrescante y natural con el toque ácido de la lima.',
        'steps': [
            'Exprimir varias limas y mezclar el jugo con agua fría.',
            'Añadir azúcar al gusto y remover hasta disolver.',
            'Servir con hielo y disfrutar.'
        ]
    },
    {
        'name': 'Marinada de Lima y Ajo para Pollo',
        'ingredients': ['lima', 'ajo', 'aceite', 'pollo'],
        'description': 'Un marinado delicioso y ácido para realzar el sabor del pollo.',
        'steps': [
            'Exprimir el jugo de lima en un bol y mezclar con ajo picado y aceite.',
            'Sumergir el pollo en la mezcla y dejar marinar por al menos 30 minutos.',
            'Cocinar a la parrilla o en sartén hasta que esté dorado y jugoso.'
        ]
    },
    {
        'name': 'Ensalada Fresca de Manzana y Zanahoria',
        'ingredients': ['manzana', 'zanahoria', 'yogur', 'azúcar'],
        'description': 'Una ensalada dulce y cremosa con un toque crujiente.',
        'steps': [
            'Rallar la zanahoria y cortar la manzana en cubos pequeños.',
            'Mezclar en un bol con yogur y un poco de azúcar.',
            'Refrigerar antes de servir para un mejor sabor.'
        ]
    },
    {
        'name': 'Manzanas Asadas con Canela y Azúcar',
        'ingredients': ['manzana', 'azúcar', 'mantequilla'],
        'description': 'Postre cálido y dulce con un toque de caramelo natural.',
        'steps': [
            'Cortar las manzanas en rodajas y colocarlas en una bandeja.',
            'Espolvorear con azúcar y agregar trocitos de mantequilla encima.',
            'Hornear a 180°C por 20 minutos hasta que estén doradas y suaves.'
        ]
    },
    {
        'name': 'Batido de Manzana y Leche',
        'ingredients': ['manzana', 'leche', 'azúcar'],
        'description': 'Bebida cremosa y nutritiva con el dulce sabor de la manzana.',
        'steps': [
            'Pelar y cortar la manzana en trozos pequeños.',
            'Licuar con leche y azúcar hasta obtener una mezcla suave.',
            'Servir frío con hielo si se desea.'
        ]
    },
    {
        'name': 'Ensalada de Remolacha y Queso',
        'ingredients': ['remolacha', 'queso', 'aceite', 'limón'],
        'description': 'Una ensalada colorida y nutritiva con un toque cítrico.',
        'steps': [
            'Cocer las remolachas hasta que estén tiernas y cortarlas en cubos.',
            'Mezclar con queso desmenuzado y un poco de aceite y jugo de limón.',
            'Servir fría como acompañamiento o plato ligero.'
        ]
    },
    {
        'name': 'Batido de Remolacha y Naranja',
        'ingredients': ['remolacha', 'naranja', 'jugo'],
        'description': 'Un batido energizante con el dulzor natural de la remolacha.',
        'steps': [
            'Cocer la remolacha hasta que esté blanda y cortarla en trozos.',
            'Licuar con jugo de naranja hasta obtener una mezcla suave.',
            'Servir frío con hielo para una bebida refrescante.'
        ]
    },
    {
        'name': 'Sopa Cremosa de Remolacha y Ajo',
        'ingredients': ['remolacha', 'ajo', 'leche', 'aceite'],
        'description': 'Una sopa rica y reconfortante con el sabor dulce de la remolacha.',
        'steps': [
            'Cocer las remolachas y triturarlas hasta obtener un puré.',
            'Saltear ajo en aceite y añadir la remolacha junto con un poco de leche.',
            'Cocinar a fuego lento hasta que la sopa esté cremosa y servir caliente.'
        ]
    },
    {
        'name': 'Ensalada Refrescante de Sandía y Pepino',
        'ingredients': ['sandía', 'pepino', 'limón', 'aceite'],
        'description': 'Una ensalada ligera y refrescante perfecta para el verano.',
        'steps': [
            'Cortar la sandía y el pepino en cubos pequeños.',
            'Mezclar en un bol y agregar jugo de limón y un chorrito de aceite.',
            'Refrigerar antes de servir para un sabor más fresco.'
        ]
    },
    {
        'name': 'Jugo Natural de Sandía',
        'ingredients': ['sandía', 'azúcar', 'jugo'],
        'description': 'Una bebida dulce y natural con el delicioso sabor de la sandía.',
        'steps': [
            'Cortar la sandía en trozos y retirar las semillas.',
            'Licuar con un poco de azúcar y agua hasta obtener una mezcla suave.',
            'Servir frío con hielo para una bebida refrescante.'
        ]
    },
    {
        'name': 'Helado Casero de Sandía',
        'ingredients': ['sandía', 'yogur', 'azúcar'],
        'description': 'Un helado cremoso y natural con el dulzor de la sandía.',
        'steps': [
            'Licuar la sandía hasta obtener un puré suave.',
            'Mezclar con yogur y azúcar al gusto.',
            'Verter en moldes y congelar por al menos 4 horas antes de disfrutar.'
        ]
    }

    # Add more recipes following the same structure
]

def find_matching_recipes(available_ingredients):
    perfect_matches = []
    partial_matches = []
    
    for recipe in RECIPE_DATABASE:
        # Count how many ingredients are available
        matching_ings = [ing for ing in recipe['ingredients'] 
                        if ing in available_ingredients]
        
        # At least one ingredient matches
        if matching_ings:
            # Perfect match (all ingredients available)
            if len(matching_ings) == len(recipe['ingredients']):
                recipe['match_type'] = 'perfect'
                perfect_matches.append(recipe)
            # Partial match (some ingredients available)
            else:
                recipe['match_type'] = 'partial'
                recipe['missing_ings'] = [ing for ing in recipe['ingredients']
                                         if ing not in available_ingredients]
                recipe['matching_ings'] = matching_ings  # Track what they have
                partial_matches.append(recipe)
    
    return {
        'perfect_matches': perfect_matches,
        'partial_matches': partial_matches
    }

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # Initialize session
    if 'detected_foods' not in session:
        session['detected_foods'] = []
    
    # Handle POST requests
    if request.method == 'POST':
        # Handle image upload and prediction
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and file and allowed_file(file.filename):
                # Process the image
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                
                # Run prediction
                results = model.predict(upload_path)
                result = results[0]
                
                # Save result image
                result_filename = f"result_{filename}"
                result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
                Image.fromarray(results[0].plot()[..., ::-1]).save(result_path)
                
                # Update detected foods
                current_detections = set()
                for box in result.boxes:
                    class_name = model.names[int(box.cls)]
                    if class_name in FOOD_MAPPING:
                        current_detections.add(FOOD_MAPPING[class_name])
                
                session['detected_foods'] = list(set(session['detected_foods']) | current_detections)
                session.modified = True
                
                return render_template('index.html',
                                    original_image=upload_path,
                                    result_image=result_path,
                                    detected_foods=sorted(session['detected_foods']),
                                    available_foods=sorted(FOOD_MAPPING.values()))
        
        # Handle list modifications
        elif 'remove_item' in request.form:
            item = request.form['remove_item']
            if item in session['detected_foods']:
                session['detected_foods'].remove(item)
                session.modified = True
        
        elif 'add_item' in request.form:
            item = request.form['food_select']
            if item not in session['detected_foods']:
                session['detected_foods'].append(item)
                session.modified = True
        
        elif 'confirm_list' in request.form:
            session['confirmed_foods'] = session['detected_foods'].copy()
            return redirect(url_for('show_recipes'))
    
    return render_template('index.html',
                         detected_foods=sorted(session['detected_foods']),
                         available_foods=sorted(FOOD_MAPPING.values()))

@app.route('/clear_list', methods=['POST'])
def clear_list():
    session['detected_foods'] = []
    session.modified = True
    return redirect(url_for('upload_file'))

@app.route('/recipes')
def show_recipes():
    if 'confirmed_foods' not in session:
        return redirect(url_for('upload_file'))
    
    available_ingredients = session['confirmed_foods']
    matches = find_matching_recipes(available_ingredients)
    
    return render_template('recipes.html',
                         ingredients=available_ingredients,
                         perfect_matches=matches['perfect_matches'],
                         partial_matches=matches['partial_matches'])

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    #app.run(debug=True)
