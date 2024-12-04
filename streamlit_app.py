import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Configuración de credenciales
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="names-project-demo")
dbNames = db.collection("names")

# Título principal
st.title("Gestión de Nombres")

# Función para cargar un nombre por su campo "name"
def loadByName(name):
    names_ref = dbNames.where(u'name', u'==', name)
    for myname in names_ref.stream():
        return myname  # Devuelve el documento encontrado
    return None  # Si no encuentra nada, retorna None

# Mostrar todos los registros
def load_all_names():
    names_ref = list(dbNames.stream())
    names_dict = list(map(lambda x: x.to_dict(), names_ref))
    return pd.DataFrame(names_dict)

# Crear un nuevo registro
st.header("Nuevo registro")
index = st.text_input("Index")
name = st.text_input("Name")
sex = st.selectbox("Select Sex", ('F', 'M', 'Other'))
submit = st.button("Crear nuevo registro")

if index and name and sex and submit:
    doc_ref = dbNames.document(name)
    doc_ref.set({
        "index": index,
        "name": name,
        "sex": sex
    })
    st.success(f"Registro '{name}' insertado correctamente.")

# Buscar un registro por nombre
st.sidebar.subheader("Buscar nombre")
nameSearch = st.sidebar.text_input("Nombre para buscar")
btnFiltrar = st.sidebar.button("Buscar")

if btnFiltrar:
    doc = loadByName(nameSearch)
    if doc is None:
        st.sidebar.error(f"El nombre '{nameSearch}' no existe.")
    else:
        st.sidebar.write(doc.to_dict())

# Eliminar un registro
st.sidebar.markdown("---")
btnEliminar = st.sidebar.button("Eliminar")
if btnEliminar:
    deletename = loadByName(nameSearch)
    if deletename is None:
        st.sidebar.error(f"El nombre '{nameSearch}' no existe.")
    else:
        dbNames.document(deletename.id).delete()
        st.sidebar.success(f"'{nameSearch}' eliminado correctamente.")

# Actualizar un registro
st.sidebar.markdown("---")
newname = st.sidebar.text_input("Nuevo nombre para actualizar")
btnActualizar = st.sidebar.button("Actualizar")
if btnActualizar:
    updatename = loadByName(nameSearch)
    if updatename is None:
        st.error(f"El nombre '{nameSearch}' no existe.")
    else:
        dbNames.document(updatename.id).update({"name": newname})
        st.success(f"Nombre actualizado correctamente a '{newname}'.")

# Mostrar todos los nombres como tabla
st.header("Lista de todos los nombres")
names_df = load_all_names()
if not names_df.empty:
    st.dataframe(names_df)
else:
    st.info("No hay registros en la base de datos.")



# ...
names_ref = list(db.collection(u'names').stream())
names_dict = list(map(lambda x: x.to_dict(), names_ref))
names_dataframe = pd.DataFrame(names_dict)
st.dataframe(names_dataframe)
