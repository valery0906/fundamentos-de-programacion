import pandas as pd

#cargar datos
ruta="https://github.com/valery0906/Valery-y-Saray---bienestar-emocional/raw/refs/heads/main/EmoSPeech_phase_2_train_public.csv"
df = pd.read_csv(ruta)

print("="*50)
print(df.head())
print("="*50)

print("="*50)
print(df.info())
print("="*50)

print("="*50)
print(df.describe())
print("-"*50)

print("="*50)
print(df.columns)
print("-"*50)

print("="*50)
print(df.isnull().sum())
print("-"*50)

print("="*50)
print(df.shape)  # filas columnas
print("-"*50)

print("="*50)
print(df['Raza'])
print("-"*50)

print("="*50)
print(df[['Raza','Especie']])
print("-"*50)

print("="*50)
print(df[df['Raza'] == 'Criollo'])
print("-"*50)