import pandas as pd
import numpy as np
import os

archivo = r'C:\Users\Luiso\Downloads\animal_data.csv'

df = pd.read_csv(archivo, sep=";")

# Diagnóstico inicial
print(df.head())
print(df.shape)
df.info()
print(df.duplicated().sum())
print("Describe: \n", df.describe())

columnas_categoricas = ["Animal type", "Country", "Gender", "Animal name", "Data compiled by"]

for col in columnas_categoricas:
    print("\nColumna:", col)
    print(df[col].unique())

for col in columnas_categoricas:
    print("\nColumna:", col)
    print(df[col].value_counts(dropna=False))   

#Inconsistencias en los tipos de datos: la variable Observation date se encuentra almacenada como texto, por lo que requiere una conversión al formato datetime para permitir operaciones relacionadas con fechas.

#Valores numéricos inválidos: se encontraron registros con valores negativos en las variables Weight kg y Body Length cm, los cuales no representan medidas físicamente posibles para los animales.

#Registros duplicados: se identificaron 167 registros duplicados, cuya permanencia podría generar una representación repetida de las observaciones y alterar los resultados estadísticos.

#Columnas con información insuficiente: la variable Animal code presenta el 100 % de sus registros vacíos, mientras que Animal name contiene 959 valores faltantes de 1.011 registros. Debido a su limitada disponibilidad de información y a que no son indispensables para el análisis general, se considera pertinente eliminar estas columnas.

#Inconsistencias categóricas: las variables Animal type y Country presentan diferencias en la escritura y representación de algunas categorías. Por ejemplo, una misma especie aparece registrada como "Red Squirrel", "Red Squirrell" y "Red Squirel". De igual manera, algunos países presentan abreviaciones o errores ortográficos. Esto requiere un proceso de estandarización para evitar agrupaciones incorrectas durante el análisis. 

#PARTE DOS LIMPIEZA DE DATOS 

df_copy = df.copy()

duplicados = df_copy.duplicated(keep=False)

print(df_copy[duplicados].sort_values(list(df_copy.columns)))
# Contar filas originales
filas_originales = len(df_copy)

# Eliminar duplicados
df_copy = df_copy.drop_duplicates()

# Contar filas después de eliminar duplicados
filas_despues = len(df_copy)

print("Filas originales:", filas_originales)
print("Filas después:", filas_despues)
print("Duplicados eliminados:", filas_originales - filas_despues)

columnas_categoricas = ["Animal type", "Country", "Gender"]

for col in columnas_categoricas:
    df_copy[col] = df_copy[col].str.strip().str.lower().str.title()

df_copy["Animal type"] = df_copy["Animal type"].replace({
    "Red Squirrell": "Red Squirrel",
    "Red Squirel": "Red Squirrel",
    "European Bisson": "European Bison",
    "European Bison™": "European Bison",
    "European Buster": "European Bison",
    "Lynx?": "Lynx",
    "Ledgehod": "Hedgehog",
    "Wedgehod": "Hedgehog"
})

df_copy["Country"] = df_copy["Country"].replace({
    "Pl": "Poland",
    "Hu": "Hungary",
    "De": "Germany",
    "Cz": "Czech Republic",
    "Czech": "Czech Republic",
    "Hungry": "Hungary"
})
for col in columnas_categoricas:
    print("\n", col)
    print(df_copy[col].value_counts(dropna=False))

columnas_numericas = ["Weight kg", "Body Length cm"]
# Un peso negativo o una longitud negativa no tienen sentido físico.En este caso podemos reemplazar esos valores por NaN y posteriormente decidir cómo tratarlos.
for col in columnas_numericas:
    df_copy.loc[df_copy[col] < 0, col] = np.nan

print(df_copy[["Weight kg", "Body Length cm"]].isna().sum())

columnas_coordenadas = ["Latitude", "Longitude"]

#Revisar valores nulos
print(df_copy[columnas_coordenadas].isna().sum())

#Calcular la mediana por país y rellenar los nulos de latitude y longitud agrupando por pais ya que se considera un valor mas cercano que la mediana general de todos los paises
for variable in columnas_coordenadas:
    mediana = df_copy.groupby("Country")[variable].transform("median")
    df_copy[variable] = df_copy[variable].fillna(mediana)
#dar formato a fechas 
df_copy["Observation date"] = pd.to_datetime(df_copy["Observation date"],format="%d.%m.%Y", errors="coerce")
print(df_copy["Observation date"].dtype)
print(df_copy["Observation date"].isna().sum())
print(df_copy.loc[df_copy["Observation date"].isna(), "Observation date"])


df_copy = df_copy.drop(columns=["Animal code"])

# SE CONSIDERA ELIMINAR COLUMNA DEBIDO A QUE NO REQUIERE ANALIZAR ANIMALES DE MANERA INVIDUAL 
df_copy = df_copy.drop(columns=["Animal name"])
# rellenar los na de genero con no determinado
df_copy["Gender"] = df_copy["Gender"].fillna("Not determined")
#completar los valores nulos con la mediana pero por animal ya que no seria lo mismo hacerlos con los valroes de los demas animales serian valores alejados
columnas_numericas = ["Weight kg", "Body Length cm"]
print(df_copy[columnas_numericas].isna().sum())

for variable in columnas_numericas:
    mediana = df_copy.groupby("Animal type")[variable].transform("median")

    print(f"La mediana por especie de {variable} es:")
    print(mediana)

    df_copy[variable] = df_copy[variable].fillna(mediana)

print(df_copy[columnas_numericas].isna().sum())

print("ver columnas:", df_copy.loc[
    df_copy["Weight kg"].isna() | df_copy["Body Length cm"].isna(),
    ["Animal type", "Weight kg", "Body Length cm"]
].to_string())
# se elimina 11 valores animal type que precisamente tiene valores nulos con longitud y peso del animal
df_copy = df_copy.dropna(subset=["Animal type"])
print(df_copy[columnas_numericas].isna().sum())
#estaba validando simplemnte aqui el tema de el pais valores anteriores y posteriores
print(df_copy["Country"].unique())
print(df_copy["Country"].value_counts(dropna=False))
print("Países nulos originales:", df["Country"].isna().sum())
print("Países nulos actuales:", df_copy["Country"].isna().sum())
print(df.loc[df["Country"].isna()].to_string())
print(df["Country"].unique())
print(df["Country"].value_counts(dropna=False))

#remplazar el valor cc que aparece en pais con la moda
print(df_copy.loc[
    df_copy["Country"] == "Cc"
].to_string())
moda_country = df_copy["Country"].mode()[0]
df_copy["Country"] = df_copy["Country"].replace("Cc", moda_country)
print("Moda utilizada:", moda_country)

print(df_copy["Country"].value_counts(dropna=False))

fechas_nulas = df_copy.loc[
    df_copy["Observation date"].isna()
]
print(fechas_nulas.to_string())
#rellenar fechas falantes con mediana
df_copy["Observation date"] = df_copy["Observation date"].fillna(
    pd.to_datetime(
        np.nanmedian(
            df_copy["Observation date"].astype("int64")
        )
    )
)

# 4. Comprobar que ya no haya fechas faltantes
print("Fechas faltantes después:", df_copy["Observation date"].isna().sum())
# 1. Columnas que vamos a tratar
# 4. Comprobar resultados
print(df_copy[columnas_coordenadas].isna().sum())

print("Valores Nulos:\n", df_copy.isnull().sum()) 


# PARTE 3. NUMPY

#Calcular la mediana del peso de los animales
mediana_peso = np.nanmedian(df_copy["Weight kg"])

print("Mediana del peso:", mediana_peso)

# Crear una nueva variable utilizando np.where()
# Clasificar los animales según su peso respecto a la mediana

df_copy["Clasificacion peso"] = np.where(df_copy["Weight kg"] >= mediana_peso,"Peso igual o superior a la mediana","Peso inferior a la mediana")

#  Comprobar los resultados
print("\nClasificación de los animales:")
print(df_copy["Clasificacion peso"].value_counts())

#  Calcular el promedio del peso utilizando NumPy
promedio_peso = np.mean(df_copy["Weight kg"])
print("\nPromedio general del peso:", promedio_peso)
print(df_copy.head())

#4 Análisis con groupby#

# Cantidad de registros por tipo de animal

observaciones_animal = df_copy.groupby("Animal type").size().sort_values(ascending=False)
print("\nObservaciones Animal:",observaciones_animal)

peso_por_animal = df_copy.groupby("Animal type")["Weight kg"].mean().sort_values(ascending=False)
print("\npesos por animal:",peso_por_animal.round(2))


longitud_por_animal = df_copy.groupby("Animal type")["Body Length cm"].mean().sort_values(ascending=False)
print("\nlongitudes por animal:", longitud_por_animal.round(2))

peso_por_pais = df_copy.groupby("Country")["Weight kg"].mean().sort_values(ascending=False)
print("\nPesos por pais:",peso_por_pais.round(2))

observaciones_pais = df_copy.groupby("Country").size().sort_values(ascending=False)
print("\nObservaciones de animales por pais por pais:",observaciones_pais)

#Conclusión 1. Distribución de las especies

#La ardilla roja representa la mayor cantidad de observaciones, 
#con 413 registros de un total de 825. equivale aproximadamente al 50 % de la base de datos,
#por lo que existe una mayor representación de esta especie frente a las demás.

#Conclusión 2. Diferencias de peso entre especies

#El bisonte europeo presenta el mayor peso promedio, 
#con 588,40 kg, mientras que la ardilla roja registra 0,30 kg.
#Esta diferencia evidencia las características físicas propias de cada especie.

#Conclusión 3. Distribución geográfica

#Polonia presenta la mayor cantidad de observaciones, 
#con 196 registros, seguida de Alemania con 178. 
#indica que la información recopilada tiene una mayor concentración en estos dos países.

#Conclusión 4. Peso promedio por país

#Polonia registra el mayor peso promedio, con 140,28 kg. Sin embargo, 
#esta diferencia puede estar relacionada con la composición de especies observadas en cada país y no necesariamente con diferencias de tamaño entre animales de una misma especie.

#Conclusión 5. Longitud de los animales

#El bisonte europeo presenta una longitud promedio de 244,24 cm,
#mientras que el erizo registra 20,22 cm. exiten diferencias importantes entre las dimensiones corporales de las especies analizadas.