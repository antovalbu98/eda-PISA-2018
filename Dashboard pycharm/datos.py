# Importar librerias

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
# display para mi merge



df = pd.read_csv('data/CP_national_en.csv', index_col = 0) # cargar datos, columna Country indice para evitrar uffef
df['Country'] = df.index.values       #Columna nueva con los valores del indice Country
df.index = list(range(len(df)))       #indice nuevo
first_col = df.pop('Country')       # saco la columna indice...
df.insert(0, 'Country', first_col, allow_duplicates = True)      # ...para insertarla a la cabeza

# ya tengo mi dataframe

df_original = df.copy()  # no trabajar con df original, pero dejarlo subido

df.drop(['Notes', 'More'], axis = 1, inplace = True)

#

df = df.melt(id_vars=['Country', 'Indicator'], value_vars=['Total', 'Men', 'Women']) #melt
df['Indicator'] = df['Indicator'] + ", " + df['variable']
df.drop(columns = 'variable', inplace = True)
df.drop_duplicates(subset=['Country', 'Indicator'], inplace=True)    #duplicados
df = df.pivot(index='Country', columns='Indicator', values= 'value')   #pivot

pisa = pd.read_excel('data/PISA.xlsx')
wdi = pd.read_excel('data/WDI.xlsx')
worldbank = pd.merge(pisa, wdi, on = 'Country Code')
worldbank.replace(to_replace = "..", value = np.nan, inplace = True )
worldbank.drop(labels = 'Country Name_y', axis = 1, inplace = True)
worldbank.iloc[:,4:] = worldbank.iloc[:,4:].apply(pd.to_numeric)
worldbank.rename({"Country Name_x" : 'Country'}, axis = 1, inplace = True)
worldbank.drop(columns = ['Time Code', 'Time'], inplace = True)

# worldbank.drop(columns = ['Time', 'Time Code'], inplace = True)

# Sacar el % de valores nulos por pais
worldbank['Null columns (%)'] = worldbank.isnull().sum(axis=1)/len(worldbank.columns[2:])
worldbank[['Country', 'Null columns (%)']].sort_values('Null columns (%)', ascending = True)

#Analisis importante, los paises tienen o muchos datos o muy pocos
    # sns.displot(worldbank, x= 'Null columns (%)');
    # print(worldbank['Null columns (%)'].describe())

#Me quedo con los paises que tienen mas datos

worldbank = worldbank[worldbank['Null columns (%)'] < 0.4]

# Anado poblacion
popu = pd.read_excel('data/population.xlsx')
popu.drop(columns = 'drop', inplace = True)

worldbank = pd.merge(worldbank, popu, on = 'Country Code')

worldbank.drop(columns = 'Country Name', inplace = True)

worldbank['Population, total [SP.POP.TOTL]'] = worldbank['Population, total [SP.POP.TOTL]'].apply(pd.to_numeric)

# reseteo el index

worldbank.index = np.arange(len(worldbank))

# borrar mierda
del df_original

#necesitan clave comun (codigos)

codigos = pd.read_excel('varios/paisesOIT.xlsx')
codigos.drop(index = 209, inplace = True)

oit = pd.merge(df, codigos, left_index = True, right_on = 'Country')

df = pd.merge(oit, worldbank, right_on = 'Country Code', left_on = 'Code')
df[['Code', 'Country_x', 'Country_y', 'Country Code']]
df.drop(columns = ['Country_y', 'Country Code'], inplace = True)

# pasar columnas de nombres y codigos al principio
first_col = df.pop('Country_x')
second_col = df.pop('Code')
df.insert(0, 'Country', first_col)
df.insert(0, 'Code', second_col)

# eliminar columnas innecesarias (local currencies ppalmente)

df.drop(columns = ['Average hourly labour cost per employee, local currency, Men',
                    'Average hourly labour cost per employee, local currency, Total',
                    'Average hourly labour cost per employee, local currency, Women',
                    'Average monthly earnings of employees, local currency, Men',
                    'Average monthly earnings of employees, local currency, Total',
                    'Average monthly earnings of employees, local currency, Women',
                    'Monthly minimum wage, local currency, Men',
                    'Monthly minimum wage, local currency, Total',
                    'Monthly minimum wage, local currency, Women',
                    'Null columns (%)'], inplace = True)

# ordenar columnas, metodo muy chulo

cols_to_order = ['Code',
                 'Country',
                 'Population, total [SP.POP.TOTL]',
                 'Adjusted net national income per capita (constant 2010 US$) [NY.ADJ.NNTY.PC.KD]',
                 'Gini index (World Bank estimate) [SI.POV.GINI]']
new_columns = cols_to_order + (df.columns.drop(cols_to_order).tolist())
df = df[new_columns]

# crear indice PISA con maths,science y reading
df['PISA Index Mean'] = df['PISA: Mean performance on the reading scale [LO.PISA.REA]']*(1/3)\
                        +df['PISA: Mean performance on the science scale [LO.PISA.SCI]']*(1/3)\
                        +df['PISA: Mean performance on the mathematics scale [LO.PISA.MAT]']*(1/3)

# indice
df.set_index(["Code",
                "Country"], inplace = True)

# multiindexar las columnas del df en funcion de si la variable corresponde a hombres, mujeres o total

columnas = [("Total","Population, total"),
    ("Total","Adjusted net national income per capita (constant 2010 US$) [NY.ADJ.NNTY.PC.KD]"),
    ("Total","Gini index"),
    ("Men","Average weekly hours actually worked per employed person, Men"),
    ("Total","Average weekly hours actually worked per employed person, Total"),
    ("Women","Average weekly hours actually worked per employed person, Women"),
    ("Men","Collective bargaining coverage rate (%), Men"),
    ("Total","Collective bargaining coverage rate (%), Total"),
    ("Women","Collective bargaining coverage rate (%), Women"),
    ("Men","Employment-population ratio (%), Men"),
    ("Total","Employment-population ratio (%), Total"),
    ("Women","Employment-population ratio (%), Women"),
    ("Men","Incidence rate of non-fatal occupational injuries (per 100'000 in reference group), Men"),
    ("Total","Incidence rate of non-fatal occupational injuries (per 100'000 in reference group), Total"),
    ("Women","Incidence rate of non-fatal occupational injuries (per 100'000 in reference group), Women"),
    ("Men","Incidence rate of occupational fatalities (per 100'000 in reference group), Men"),
    ("Total","Incidence rate of occupational fatalities (per 100'000 in reference group), Total"),
    ("Women","Incidence rate of occupational fatalities (per 100'000 in reference group), Women"),
    ("Men","LU3: Combined rate of unemployment and potential labour force (%), Men"),
    ("Total","LU3: Combined rate of unemployment and potential labour force (%), Total"),
    ("Women","LU3: Combined rate of unemployment and potential labour force (%), Women"),
    ("Men","LU4: Composite rate of labour underutilization (%), Men"),
    ("Total","LU4: Composite rate of labour underutilization (%), Total"),
    ("Women","LU4: Composite rate of labour underutilization (%), Women"),
    ("Men","Labour force participation rate (%), Men"),
    ("Total","Labour force participation rate (%), Total"),
    ("Women","Labour force participation rate (%), Women"),
    ("Men","Population covered by at least one social protection benefit (%), Men"),
    ("Total","Population covered by at least one social protection benefit (%), Total"),
    ("Women","Population covered by at least one social protection benefit (%), Women"),
    ("Men","Share of agriculture (%), Men"),
    ("Total","Share of agriculture (%), Total"),
    ("Women","Share of agriculture (%), Women"),
    ("Men","Share of employed working more than 48 hours per week (%), Men"),
    ("Total","Share of employed working more than 48 hours per week (%), Total"),
    ("Women","Share of employed working more than 48 hours per week (%), Women"),
    ("Men","Share of industry (%), Men"),
    ("Total","Share of industry (%), Total"),
    ("Women","Share of industry (%), Women"),
    ("Men","Share of informal employment -- Harmonized series (%), Men"),
    ("Total","Share of informal employment -- Harmonized series (%), Total"),
    ("Women","Share of informal employment -- Harmonized series (%), Women"),
    ("Men","Share of managers, professionals (incl. associates) and technicians (%), Men"),
    ("Total","Share of managers, professionals (incl. associates) and technicians (%), Total"),
    ("Women","Share of managers, professionals (incl. associates) and technicians (%), Women"),
    ("Men","Share of services (%), Men"),
    ("Total","Share of services (%), Total"),
    ("Women","Share of services (%), Women"),
    ("Men","Share of youth not in employment, education or training (%), Men"),
    ("Total","Share of youth not in employment, education or training (%), Total"),
    ("Women","Share of youth not in employment, education or training (%), Women"),
    ("Men","Trade union density rate (%), Men"),
    ("Total","Trade union density rate (%), Total"),
    ("Women","Trade union density rate (%), Women"),
    ("Men","Unemployment rate (%), Men"),
    ("Total","Unemployment rate (%), Total"),
    ("Women","Unemployment rate (%), Women"),
    ("Men","Unemployment rate, youth (%), Men"),
    ("Total","Unemployment rate, youth (%), Total"),
    ("Women","Unemployment rate, youth (%), Women"),
    ("Women","PISA: Mean performance on the science scale. Female [LO.PISA.SCI.FE]"),
    ("Men","PISA: Mean performance on the reading scale. Male [LO.PISA.REA.MA]"),
    ("Women","PISA: Mean performance on the mathematics scale. Female [LO.PISA.MAT.FE]"),
    ("Total","PISA: Mean performance on the reading scale [LO.PISA.REA]"),
    ("Total","PISA: Mean performance on the mathematics scale [LO.PISA.MAT]"),
    ("Men","PISA: Mean performance on the mathematics scale. Male [LO.PISA.MAT.MA]"),
    ("Women","PISA: Mean performance on the reading scale. Female [LO.PISA.REA.FE]"),
    ("Total","PISA: Mean performance on the science scale [LO.PISA.SCI]"),
    ("Men","PISA: Mean performance on the science scale. Male [LO.PISA.SCI.MA]"),
    ("Total","PISA: Distribution of Mathematics Scores: 50th Percentile Score [LO.PISA.MAT.P50]"),
    ("Total","PISA: Distribution of Mathematics Scores: 75th Percentile Score [LO.PISA.MAT.P75]"),
    ("Total","PISA: Distribution of Mathematics Scores: 10th Percentile Score [LO.PISA.MAT.P10]"),
    ("Total","PISA: Distribution of Mathematics Scores: 95th Percentile Score [LO.PISA.MAT.P95]"),
    ("Total","PISA: Distribution of Mathematics Scores: 25th Percentile Score [LO.PISA.MAT.P25]"),
    ("Total","PISA: Distribution of Mathematics Scores: 5th Percentile Score [LO.PISA.MAT.P05]"),
    ("Total","PISA: Distribution of Mathematics Scores: 90th Percentile Score [LO.PISA.MAT.P90]"),
    ("Total","PISA: Distribution of Reading Scores: 10th Percentile Score [LO.PISA.REA.P10]"),
    ("Total","PISA: Distribution of Reading Scores: 50th Percentile Score [LO.PISA.REA.P50]"),
    ("Total","PISA: Distribution of Reading Scores: 75th Percentile Score [LO.PISA.REA.P75]"),
    ("Total","PISA: Distribution of Reading Scores: 25th Percentile Score [LO.PISA.REA.P25]"),
    ("Total","PISA: Distribution of Reading Scores: 5th Percentile Score [LO.PISA.REA.P05]"),
    ("Total","PISA: Distribution of Reading Scores: 90th Percentile Score [LO.PISA.REA.P90]"),
    ("Total","PISA: Distribution of Science Scores: 95th Percentile Score [LO.PISA.SCI.P95]"),
    ("Total","PISA: Distribution of Science Scores: 75th Percentile Score [LO.PISA.SCI.P75]"),
    ("Total","PISA: Distribution of Science Scores: 50th Percentile Score [LO.PISA.SCI.P50]"),
    ("Total","PISA: Distribution of Science Scores: 10th Percentile Score [LO.PISA.SCI.P10]"),
    ("Total","PISA: Distribution of Reading Scores: 95th Percentile Score [LO.PISA.REA.P95]"),
    ("Total","PISA: Distribution of Science Scores: 25th Percentile Score [LO.PISA.SCI.P25]"),
    ("Total","PISA: Distribution of Science Scores: 5th Percentile Score [LO.PISA.SCI.P05]"),
    ("Total","PISA: Distribution of Science Scores: 90th Percentile Score [LO.PISA.SCI.P90]"),
    ("Total","Labor force with advanced education (% of total working-age population with advanced education) [SL.TLF.ADVN.ZS]"),
    ("Women","Labor force with advanced education, female (% of female working-age population with advanced education) [SL.TLF.ADVN.FE.ZS]"),
    ("Men","Labor force with advanced education, male (% of male working-age population with advanced education) [SL.TLF.ADVN.MA.ZS]"),
    ("Total","Labor force with basic education (% of total working-age population with basic education) [SL.TLF.BASC.ZS]"),
    ("Women","Labor force with basic education, female (% of female working-age population with basic education) [SL.TLF.BASC.FE.ZS]"),
    ("Men","Labor force with basic education, male (% of male working-age population with basic education) [SL.TLF.BASC.MA.ZS]"),
    ("Total","Labor force with intermediate education (% of total working-age population with intermediate education) [SL.TLF.INTM.ZS]"),
    ("Women","Labor force with intermediate education, female (% of female working-age population with intermediate education) [SL.TLF.INTM.FE.ZS]"),
    ("Men","Labor force with intermediate education, male (% of male working-age population with intermediate education) [SL.TLF.INTM.MA.ZS]"),
    ("Total","PISA Index Mean")]

df.columns = pd.MultiIndex.from_tuples(columnas)

# cross section para tener 3 df: uno de mujeres, uno de hombres, uno total
dftotales = df.xs('Total', axis=1, level=0)
dfhombres = df.xs('Men', axis=1, level=0)
dfmujeres = df.xs('Women', axis=1, level=0)

dftotales.reset_index(level=['Country'], inplace = True)
dfhombres.reset_index(level=['Country'], inplace = True)
dfmujeres.reset_index(level=['Country'], inplace = True)

# drop, muchos missings
dftotales.drop(columns = "Share of informal employment -- Harmonized series (%), Total", inplace = True)



#arreglar el missing de Espana
dftotales.at['ESP', 'PISA Index Mean'] = \
dftotales[dftotales['Country'] == 'Spain']['PISA: Mean performance on the mathematics scale [LO.PISA.MAT]']*0.5 + \
dftotales[dftotales['Country'] == 'Spain']['PISA: Mean performance on the science scale [LO.PISA.SCI]']*0.5