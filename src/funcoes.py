from src.arqImport import *
from src.listasCompartilhadas import *

def regiao(nome, tipo, listaRegiao):
    encontrado = False  # Variável auxiliar para rastrear se o nome já foi encontrado
    for x in listaRegiao:
        if x.cidade == nome:
            encontrado = True
            if tipo == 'Non Resedential':
                x.incrementar_ocorrenciax(1)
            else:
                x.incrementar_ocorrenciay(1)
            x.somarTotal()
            break

    if not encontrado:  # Se o nome não foi encontrado, adicione-o à lista
        aux = Infos(nome, 0, 0, 0)
        if tipo == 'Non Resedential':
            aux.incrementar_ocorrenciax(1)
        else:
            aux.incrementar_ocorrenciay(1)
        aux.somarTotal()
        listaRegiao.append(aux)

def coordenadas(lista):
    lista2 = []
    with open('input/fullCoordenadas.csv', 'r') as arq_csv:
        read = csv.DictReader(arq_csv)
        for linha in read:
            nome = linha['nick']
            latitude = linha['lati']
            longitude = linha['long']
            latitude = latitude.replace(',', '.')
            longitude = longitude.replace(',', '.')

            #aqui faz a poda das regioes sem localização ou desertos...
            for x in lista:
                if x.cidade == nome:
                    aux = Infos(nome,x.ocorrenciax,x.ocorrenciay,x.total)
                    aux.coordenas(latitude,longitude)
                    lista2.append(aux)
                    break
    return lista2

def determinar_cor(cidade):
    if cidade.total >= 10:
        cor = 'red'
        global color_red 
        color_red = color_red + 1
    elif 5 < cidade.total < 10:
        cor = 'orange'
        global color_orange 
        color_orange = color_orange + 1
    elif cidade.total <= 5:
        cor = 'yellow'
        global color_yellow 
        color_yellow = color_yellow + 1
    else:
        cor = 'lightblue'
    return cor

def removerNos(G):
    nos_a_remover = [node for node, cor in nx.get_node_attributes(G, 'cor').items() if cor != 'red']
    G.remove_nodes_from(nos_a_remover)

def grafo(lista,start):
    G = nx.Graph()
    edge_data = {}
    edge_dataColor = {}
    
    for cidade_info in lista:
        nome = cidade_info.cidade
        ataque = cidade_info.total  
        cor =  determinar_cor(cidade_info)
        edge_dataColor[(cidade_info.cidade, cidade_info.cidade)] = cor
        G.add_node(nome, latitude=float(cidade_info.latitude), longitude=float(cidade_info.longitude), total = ataque, cor = cor)

    for cidade_info1 in lista:
        for cidade_info2 in lista:
            if cidade_info1 != cidade_info2:
                coords1 = (cidade_info1.latitude, cidade_info1.longitude)
                coords2 = (cidade_info2.latitude, cidade_info2.longitude)
                point1 = Point(coords1)
                point2 = Point(coords2)
                distancia = geodesic(point1, point2).kilometers
                G.add_edge(cidade_info1.cidade, cidade_info2.cidade, weight=distancia)
                edge_data[(cidade_info1.cidade, cidade_info2.cidade)] = distancia
        
    print("Localidades: ", color_red," vermelho,", color_orange," laranja,", color_yellow," amarelo")

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color=[G.nodes[v].get('cor', 'lightblue') for v in G.nodes], font_color='black', font_weight='bold', node_size=700)
    plt.title("Grafo Original")
    plt.show()

    removerNos(G)
    salvarCSVapenasVermelhos(G)
    nx.draw(G, pos, with_labels=True, node_color=[G.nodes[v].get('cor', 'lightblue') for v in G.nodes], font_color='black', font_weight='bold', node_size=700)
    plt.title("Grafo Pos corte")
    plt.show()

    nome, maior_ataque_bfs = bfs_maior_ataque(G,start)
    print(f'O nó {nome} com o maior ataque tem valor: {maior_ataque_bfs}')

    agm = nx.minimum_spanning_tree(G)
    pos = nx.spring_layout(agm)
    nx.draw(agm, pos, with_labels=True, node_color=[G.nodes[v].get('cor', 'lightblue') for v in agm.nodes], font_color='black', font_weight='bold', node_size=700)
    labels_agm = nx.get_edge_attributes(agm, 'weight')
    formatted_labels_agm = {edge: f"{weight:.0f}" for edge, weight in labels_agm.items()}
    nx.draw_networkx_edge_labels(agm, pos, edge_labels=formatted_labels_agm)
    plt.title("Árvore Geradora Mínima do Subgrafo")
    plt.show()

    salvarCSV(edge_data)
    salvarCSV2(edge_dataColor)
  
def salvarCSV(edge_data):
    csv_file = "output/graph.csv"

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Source', 'Target', 'Weight'])
        for (cidade1, cidade2), distancia in edge_data.items():
            writer.writerow([cidade1, cidade2, distancia])

    print(f"As informações foram salvas no arquivo CSV: {csv_file}")

def salvarCSV2(edge_data):
    csv_file = "output/graphColor.csv"

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Id', 'Label', 'Cor'])
        for (cidade1, cidade2), cor in edge_data.items():
            writer.writerow([cidade1, cidade2, cor])

    print(f"As informações foram salvas no arquivo CSV: {csv_file}")

def salvarCSVapenasVermelhos(G):
    with open('output/infGraphJustRed.csv', 'w', newline='') as csvfile:
        # Crie um objeto escritor CSV
        csv_writer = csv.writer(csvfile)

        # Escreva o cabeçalho do CSV
        csv_writer.writerow(['Label','Source', 'Target', 'Weight'])

        # Iterar sobre as arestas do grafo e escrever as informações no arquivo CSV
        for edge in G.edges(data=True):
            cidade1, cidade2, data = edge
            peso = data['weight']

            csv_writer.writerow([cidade1,cidade1, cidade2, peso])

def salvarCSV3(lista):
    csv_file = "output/FullNos.csv"

    # Abrir o arquivo CSV em modo de escrita
    with open(csv_file, mode='w', newline='') as file:
        # Criar um escritor CSV
        writer = csv.writer(file)

        # Escrever o cabeçalho (opcional, dependendo dos requisitos)
        writer.writerow(['Id'])

        # Iterar sobre as entradas do grafo_dict e escrever no arquivo CSV
        for x in lista:
            writer.writerow([x.cidade])

    print(f"As informações foram salvas no arquivo CSV: {csv_file}")

def gerar_TodasLista():
    with open('input/demolition.csv', 'r') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)
        for linha in leitor_csv:
            nome = linha['locality']
            distrito = linha['district']
            tipo = linha['type_of_sturcture']
            
            regiao(nome,tipo,Full_lista)

            if distrito == 'Hebron':  
                regiao(nome,tipo,listaHebron)
            
            if distrito == 'Tulkarm': 
                regiao(nome,tipo,listaTulkarm)
            
            if distrito == 'al-Quds': 
                regiao(nome,tipo,listaAlQuds)

            if distrito == 'Jericho': 
                regiao(nome,tipo,listaJericho)
            
            if distrito == 'Jenin': 
                regiao(nome,tipo,listaJenin)
            
            if distrito == 'Salfit': 
                regiao(nome,tipo,listaSalfit)
            
            if distrito == 'Nablus': 
                regiao(nome,tipo,listaNablus)

            if distrito == 'Bethlehem': 
                regiao(nome,tipo,listaBethlehem)

            if distrito == 'Tubas': 
                regiao(nome,tipo,listaTubas)

            if distrito == 'Qalqiliya': 
                regiao(nome,tipo,listaQalqiliya)

            if distrito == 'Ramallah and al-Bira': 
                regiao(nome,tipo,listaRamallah)

def adicionar_Coordenadas():
    global listaHebron, listaTulkarm, listaAlQuds, listaJericho, listaJenin, listaSalfit, listaNablus, listaBethlehem, listaTubas, listaQalqiliya, listaRamallah, Full_lista
    listaHebron = coordenadas(listaHebron)
    listaTulkarm = coordenadas(listaTulkarm)
    listaAlQuds = coordenadas(listaAlQuds)
    listaJericho = coordenadas(listaJericho)
    listaJenin = coordenadas(listaJenin)
    listaSalfit = coordenadas(listaSalfit)
    listaNablus = coordenadas(listaNablus)
    listaBethlehem = coordenadas (listaBethlehem)
    listaTubas = coordenadas(listaTubas)
    listaQalqiliya = coordenadas(listaQalqiliya)
    listaRamallah = coordenadas(listaRamallah)

def bfs_maior_ataque(grafo, inicio):
    fila = deque([(inicio, grafo.nodes[inicio]['total'])])
    visitados = set()
    numeroAtaque = float('-inf')
    nome = None

    while fila:
        vertice_atual, ataque_atual = fila.popleft()
        visitados.add(vertice_atual)

        # Verificar o atributo 'ataque' do nó atual
        if ataque_atual > numeroAtaque:
            numeroAtaque = ataque_atual
            nome = vertice_atual

        for vizinho in grafo.neighbors(vertice_atual):
            if vizinho not in visitados:
                fila.append((vizinho, grafo.nodes[vizinho]['total']))

    return nome, numeroAtaque

def infos():
    Full_lista = listaHebron + listaTulkarm + listaAlQuds + listaJericho + listaJenin + listaSalfit + listaNablus + listaBethlehem + listaTubas + listaQalqiliya + listaRamallah
    case = int(input("Digite o case: "))

    if(case == 1):
        print("Quantidade de locais no distrito de Hebron processados: ",len(listaHebron))
        grafo(listaHebron,"Hebron")
    elif(case == 2):
        print("Quantidade de locais no distrito de Tulkarm processados: ",len(listaTulkarm))
        grafo(listaTulkarm,"Tulkarm")
    elif(case == 3):
        print("Quantidade de locais no distrito de Al-Quds processados: ",len(listaAlQuds))
        grafo(listaAlQuds,"Hizma")
    elif(case == 4):
        print("Quantidade de locais no distrito de Jericho processados: ",len(listaJericho))
        grafo(listaJericho,"Jericho")
    elif(case == 5):
        print("Quantidade de locais no distrito de Jenin processados: ",len(listaJenin))
        grafo(listaJenin,"Jenin R.C.")
    elif(case == 6):
        print("Quantidade de locais no distrito de Salfit processados: ",len(listaSalfit))
        grafo(listaSalfit,"Haris")
    elif(case == 7):
        print("Quantidade de locais no distrito de Nablus processados: ",len(listaNablus))
        grafo(listaNablus,"Duma")
    elif(case == 8):
        print("Quantidade de locais no distrito de Bethlehem processados: ",len(listaBethlehem))
        grafo(listaBethlehem,"Nahhalin")
    elif(case == 9):
        print("Quantidade de locais no distrito de Tubas processados: ",len(listaTubas))
        grafo(listaTubas,"Bardalah")
    elif(case == 10):
        #sem regiao
        print("Quantidade de locais no distrito de Qalqiliya processados: ",len(listaQalqiliya))
        #grafo(listaQalqiliya,"")
    elif(case == 11):
        print("Quantidade de locais no distrito de Ramallah processados: ",len(listaRamallah))
        grafo(listaRamallah,"al-Mughayir")
    elif(case == 12):
        print("Quantidade de locais no Estado da Palestina processados: ",len(Full_lista))
        grafo(Full_lista,"Hebron")
    
    