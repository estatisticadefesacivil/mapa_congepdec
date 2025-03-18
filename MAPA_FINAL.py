import os
import pandas as pd
import folium
from folium.plugins import Search
from PIL import Image
from folium import CustomIcon

# Carregar os dados do seu arquivo Excel
file_path = "Locais - Manaus.xlsx"
dataset = pd.read_excel(file_path)

# Substituir vírgulas por ponto e garantir que latitude e longitude sejam do tipo float
dataset['LONGITUDE'] = dataset['LONGITUDE'].replace(',', '.', regex=True).astype(float)
dataset['LATITUDE'] = dataset['LATITUDE'].replace(',', '.', regex=True).astype(float)

# Criar o mapa com o tema CartoDB VoyagerLabelsUnder
mapa = folium.Map(
    location=[dataset['LATITUDE'].mean(), dataset['LONGITUDE'].mean()],
    zoom_start=14,
    tiles='CartoDB.VoyagerLabelsUnder'  # Tema CartoDB VoyagerLabelsUnder
)

# Criar um FeatureGroup para os marcadores (sem o MarkerCluster)
fg = folium.FeatureGroup(name="Locais").add_to(mapa)

# Função para retornar o caminho local do ícone PNG baseado na legenda
def get_icon_path(legenda):
    icon_paths = {
        'Ponto Turístico': "ponto_turistico.png",
        'Hospital': "hospital.png",
        'Restaurante': "restaurante.png",
        'Local do Evento': "local_evento.png",
        'Sede da Defesa Civil': "defesa.png",
        'Hotel': "hotel.png",
        'Aeroporto': "Aeroporto.png"
    }
    
    return icon_paths.get(legenda, "icons/default.png")

# Dicionário para armazenar os marcadores por nome (para referenciar o popup posteriormente)
markers = {}

# Adicionar marcadores com ícones personalizados ao mapa
for idx, row in dataset.iterrows():
    legenda = row['Legenda']  # Coluna que contém o tipo do local
    icon_path = get_icon_path(legenda)  # Obtém o caminho do ícone

    if os.path.exists(icon_path):
        try:
            # Carregar a imagem do ícone usando PIL (Pillow)
            icon_image = Image.open(icon_path)
            icon_image = icon_image.convert("RGBA")  # Converte para RGBA para garantir a transparência
            
            # Salvar a imagem temporariamente com a extensão correta para folium
            temp_icon_path = "temp_icon.png"
            icon_image.save(temp_icon_path, "PNG")

            # Usando o CustomIcon do folium com uma imagem local (PNG)
            icon = CustomIcon(
                icon_image=temp_icon_path,
                icon_size=(30, 30),  # Ajuste o tamanho do ícone
                icon_anchor=(15, 30),  # Ancoragem do ícone
                popup_anchor=(0, -30)  # Ajuste do popup
            )

            # Criar o conteúdo do popup com descrição e foto
            descricao = row['Localização'] if 'Localização' in row else "Descrição não disponível"
            photo_url = row['foto'] if 'foto' in row else None  # Coluna 'Foto' contendo o caminho da imagem

            # HTML do popup com CSS para aumentar a fonte
            popup_content = f"""
            <div style="font-size: 18px;">  <!-- Aumentando a fonte do conteúdo -->
                <b style="font-size: 20px; color: #0044cc;">{row['name']}</b><br>  <!-- Aumentando a fonte do nome -->
                <p style="font-size: 16px; color: #333;">{descricao}</p>  <!-- Aumentando a fonte da descrição -->
            </div>
            """

            # Verifique se há uma URL de foto válida
            if photo_url:
                # Verifique se a foto é um caminho local ou uma URL
                if os.path.exists(photo_url):  # Caso seja um caminho local
                    popup_content += f'<img src="{photo_url}" alt="Foto do Local" style="width:100%; height:auto;">'
                else:  # Caso seja uma URL
                    popup_content += f'<img src="{photo_url}" alt="Foto do Local" style="width:100%; height:auto;">'

            # Criar o marcador e adicionar ao mapa
            marker = folium.Marker(
                location=[row["LATITUDE"], row["LONGITUDE"]],
                popup=folium.Popup(popup_content, max_width=500),  # Popup com conteúdo HTML
                tooltip=row["name"],  # Mostra nome ao passar o mouse
                icon=icon,  # Agora passando o CustomIcon diretamente
                name=row["name"]  # Definindo nome para busca
            ).add_to(fg)

            # Armazenar o marcador para referência futura
            markers[row['name']] = marker

        except Exception as e:
            print(f"Erro ao carregar o ícone para {row['name']}: {e}")
    else:
        print(f"Ícone não encontrado para {legenda}: {icon_path}")

# Adicionar sistema de busca no mapa
Search(
    layer=fg,  # A camada agora é o FeatureGroup (sem o MarkerCluster)
    search_label="name",  # Busca pelo nome
    placeholder="Buscar local...",
    collapsed=False
).add_to(mapa)


# Código CSS para estilizar a barra de pesquisa
custom_css = """
<style>
    .leaflet-control-search {
        font-size: 14px !important;
        background-color: white !important;
        border: 1px solid #8cb1d9 !important;
        border-radius: 8px !important;
        padding: 5px !important;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2) !important;
    }
    .leaflet-control-search input {
        border: none !important;
        outline: none !important;
        font-size: 14px !important;
        padding: 8px !important;
    }
</style>
"""

# Adicionar o CSS personalizado ao mapa
mapa.get_root().html.add_child(folium.Element(custom_css))

# Salvar o mapa como um arquivo HTML
mapa.save('MAPA_FINAL.html')

print("Mapa HTML com busca gerado com sucesso!")
